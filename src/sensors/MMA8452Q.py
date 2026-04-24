from math import atan2, sqrt
import smbus2
import time


class MMA8452Q:
    SLAVE_ADDR_HIGH = 0b0011101
    SLAVE_ADDR_LOW  = 0b0011100

    REG_CTRL1 = 0x2A
    REG_XYZ_DATA_CFG = 0x0E
    REG_OUT_X_MSB = 0x01
    REG_WHOAMI = 0x0D
    WHOAMI_EXPECTED = 0x2A

    def __init__(self, bus=11, address=SLAVE_ADDR_LOW, scale=2):
        self.bus = smbus2.SMBus(bus)
        self.address = address

        if scale == 4:
            self.scale_bits = 0b01
            self.scale = 4
        elif scale == 8:
            self.scale_bits = 0b10
            self.scale = 8
        else:
            self.scale_bits = 0b00
            self.scale = 2

        # filtering
        self.filter_len = 10
        self.bufX = [0.0] * self.filter_len
        self.bufY = [0.0] * self.filter_len
        self.bufZ = [0.0] * self.filter_len
        self.buf_i = 0

        self._enter_standby()
        self._configure_scale()
        self._enter_active()

        # Two independent rotation matrices
        self.R_level = [[1,0,0],[0,1,0],[0,0,1]]
        self.R_horizon = [[1,0,0],[0,1,0],[0,0,1]]

    # -------------------------------------------------------
    # Detection
    # -------------------------------------------------------

    @staticmethod
    def detect(bus_number):
        try:
            bus = smbus2.SMBus(bus_number)
        except:
            return None

        for addr in (MMA8452Q.SLAVE_ADDR_LOW, MMA8452Q.SLAVE_ADDR_HIGH):
            try:
                whoami = bus.read_byte_data(addr, MMA8452Q.REG_WHOAMI)
                if whoami == MMA8452Q.WHOAMI_EXPECTED:
                    bus.close()
                    return addr
            except:
                pass

        bus.close()
        return None

    # -------------------------------------------------------
    # Low-level I2C
    # -------------------------------------------------------

    def _read_register(self, reg):
        return self.bus.read_byte_data(self.address, reg)

    def _write_register(self, reg, value):
        self.bus.write_byte_data(self.address, reg, value)

    def _enter_standby(self):
        ctrl1 = self._read_register(self.REG_CTRL1)
        self._write_register(self.REG_CTRL1, ctrl1 & 0xFE)

    def _enter_active(self):
        ctrl1 = self._read_register(self.REG_CTRL1)
        self._write_register(self.REG_CTRL1, ctrl1 | 0x01)

    def _configure_scale(self):
        cfg = self._read_register(self.REG_XYZ_DATA_CFG)
        cfg &= 0xFC
        cfg |= self.scale_bits
        self._write_register(self.REG_XYZ_DATA_CFG, cfg)

    # -------------------------------------------------------
    # Raw reading
    # -------------------------------------------------------

    def read_raw_6bytes(self):
        return self.bus.read_i2c_block_data(self.address, self.REG_OUT_X_MSB, 6)

    @staticmethod
    def _convert_msb_lsb(msb, lsb):
        val = (msb << 4) | (lsb >> 4)
        if msb & 0x80:
            val |= 0xF000
        return val if val < 32768 else val - 65536

    def read_acceleration_raw(self):
        d = self.read_raw_6bytes()

        x = self._convert_msb_lsb(d[0], d[1])
        y = self._convert_msb_lsb(d[2], d[3])
        z = self._convert_msb_lsb(d[4], d[5])

        counts_per_g = 1024.0 * 2 / self.scale

        ax = x / counts_per_g
        ay = y / counts_per_g
        az = z / counts_per_g

        # moving average
        self.bufX[self.buf_i] = ax
        self.bufY[self.buf_i] = ay
        self.bufZ[self.buf_i] = az

        self.buf_i = (self.buf_i + 1) % self.filter_len

        ax = sum(self.bufX) / self.filter_len
        ay = sum(self.bufY) / self.filter_len
        az = sum(self.bufZ) / self.filter_len

        return ax, ay, az

    # -------------------------------------------------------
    # Rotation helpers
    # -------------------------------------------------------

    def _rotate_with_matrix(self, x, y, z, R):
        return (
            R[0][0]*x + R[0][1]*y + R[0][2]*z,
            R[1][0]*x + R[1][1]*y + R[1][2]*z,
            R[2][0]*x + R[2][1]*y + R[2][2]*z
        )

    def _compute_calibration_matrix(self, samples=50, delay=0.01):
        sx = sy = sz = 0.0

        for _ in range(samples):
            ax, ay, az = self.read_acceleration_raw()
            sx += ax
            sy += ay
            sz += az
            time.sleep(delay)

        gx = sx / samples
        gy = sy / samples
        gz = sz / samples

        norm = sqrt(gx*gx + gy*gy + gz*gz)
        gx /= norm
        gy /= norm
        gz /= norm

        tx, ty, tz = 0.0, 0.0, 1.0

        vx = gy * tz - gz * ty
        vy = gz * tx - gx * tz
        vz = gx * ty - gy * tx

        s = sqrt(vx*vx + vy*vy + vz*vz)
        c = gx*tx + gy*ty + gz*tz

        if s < 1e-6:
            return [[1,0,0],[0,1,0],[0,0,1]]

        vx /= s
        vy /= s
        vz /= s

        K = [
            [0, -vz, vy],
            [vz, 0, -vx],
            [-vy, vx, 0]
        ]

        def matmul(A, B):
            return [[sum(A[i][k]*B[k][j] for k in range(3)) for j in range(3)] for i in range(3)]

        I = [[1,0,0],[0,1,0],[0,0,1]]
        K2 = matmul(K, K)

        return [
            [
                I[i][j] + K[i][j]*s + K2[i][j]*(1-c)
                for j in range(3)
            ]
            for i in range(3)
        ]

    # -------------------------------------------------------
    # Calibration
    # -------------------------------------------------------

    def calibrate_level(self, samples=50, delay=0.01):
        self.R_level = self._compute_calibration_matrix(samples, delay)

    def calibrate_artificial_horizon(self, samples=50, delay=0.01):
        self.R_horizon = self._compute_calibration_matrix(samples, delay)

    # -------------------------------------------------------
    # Orientation outputs
    # -------------------------------------------------------

    def read_gyro_level(self):
        ax, ay, az = self.read_acceleration_raw()
        ax, ay, az = self._rotate_with_matrix(ax, ay, az, self.R_level)

        roll  = atan2(ay, az) * 57.2958
        pitch = atan2(-ax, sqrt(ay*ay + az*az)) * 57.2958

        return roll, pitch

    def read_gyro_artificial_horizon(self):
        ax, ay, az = self.read_acceleration_raw()
        ax, ay, az = self._rotate_with_matrix(ax, ay, az, self.R_horizon)

        roll  = atan2(ay, az) * 57.2958
        pitch = atan2(-ax, sqrt(ay*ay + az*az)) * 57.2958

        return roll, pitch

    def read_acceleration_level(self):
        ax, ay, az = self.read_acceleration_raw()
        return self._rotate_with_matrix(ax, ay, az, self.R_level)

    def read_acceleration_artificial_horizon(self):
        ax, ay, az = self.read_acceleration_raw()
        return self._rotate_with_matrix(ax, ay, az, self.R_horizon)

    # backward compatibility
    def read_acceleration(self):
        return self.read_acceleration_level()

    # -------------------------------------------------------
    # Cleanup
    # -------------------------------------------------------

    def close(self):
        if self.bus is None:
            return
        ctrl1 = self._read_register(self.REG_CTRL1)
        self._write_register(self.REG_CTRL1, ctrl1 & 0xFE)
        self.bus.close()
        self.bus = None

    def __del__(self):
        self.close()