from math import atan2, sqrt, radians, sin, cos
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

        self._enter_standby()
        self._configure_scale()
        self._enter_active()

        # Identity rotation until calibrated
        self.R = [
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1]
        ]

    # -------------------------------------------------------
    # Detection
    # -------------------------------------------------------

    @staticmethod
    def detect(bus_number):
        """
        Returns the I2C address if an MMA8452Q responds on the given bus.
        """
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
    # Reading raw data
    # -------------------------------------------------------

    def read_raw_6bytes(self):
        return self.bus.read_i2c_block_data(self.address, self.REG_OUT_X_MSB, 6)

    @staticmethod
    def _convert_msb_lsb(msb, lsb):
        val = (msb << 4) | (lsb >> 4)
        if msb & 0x80:
            val |= 0xF000
        return val if val < 32768 else val - 65536

    def read_acceleration(self):
        d = self.read_raw_6bytes()

        x = self._convert_msb_lsb(d[0], d[1])
        y = self._convert_msb_lsb(d[2], d[3])
        z = self._convert_msb_lsb(d[4], d[5])

        counts_per_g = 1024.0 * 2 / self.scale

        return (
            x / counts_per_g,
            y / counts_per_g,
            z / counts_per_g
        )

    # -------------------------------------------------------
    # Calibration & rotation math
    # -------------------------------------------------------

    def calibrate_level(self, samples=50, delay=0.01):
        """
        Reads several samples and defines that orientation as 0°.
        Call this while the device is in the desired 'level' position.
        """
        sx = sy = sz = 0.0

        for _ in range(samples):
            ax, ay, az = self.read_acceleration()
            sx += ax
            sy += ay
            sz += az
            time.sleep(delay)

        gx = sx / samples
        gy = sy / samples
        gz = sz / samples

        # Normalize gravity vector
        norm = sqrt(gx*gx + gy*gy + gz*gz)
        gx /= norm
        gy /= norm
        gz /= norm

        # Target gravity vector
        tx, ty, tz = 0.0, 0.0, 1.0

        # Axis-angle rotation
        vx = gy * tz - gz * ty
        vy = gz * tx - gx * tz
        vz = gx * ty - gy * tx

        s = sqrt(vx*vx + vy*vy + vz*vz)
        c = gx*tx + gy*ty + gz*tz

        if s < 1e-6:
            self.R = [[1,0,0],[0,1,0],[0,0,1]]
            return

        vx /= s
        vy /= s
        vz /= s

        K = [
            [ 0, -vz,  vy],
            [ vz,  0, -vx],
            [-vy, vx,   0]
        ]

        def matmul(A, B):
            return [[sum(A[i][k]*B[k][j] for k in range(3)) for j in range(3)] for i in range(3)]

        I = [[1,0,0],[0,1,0],[0,0,1]]
        K2 = matmul(K, K)

        self.R = [
            [
                I[i][j] + K[i][j]*s + K2[i][j]*(1-c)
                for j in range(3)
            ]
            for i in range(3)
        ]

    def _rotate(self, x, y, z):
        return (
            self.R[0][0]*x + self.R[0][1]*y + self.R[0][2]*z,
            self.R[1][0]*x + self.R[1][1]*y + self.R[1][2]*z,
            self.R[2][0]*x + self.R[2][1]*y + self.R[2][2]*z
        )

    # -------------------------------------------------------
    # Orientation output
    # -------------------------------------------------------

    def read_gyro(self):
        ax, ay, az = self.read_acceleration()
        ax, ay, az = self._rotate(ax, ay, az)

        roll  = atan2(ay, az) * 57.2958
        pitch = atan2(-ax, sqrt(ay*ay + az*az)) * 57.2958

        return roll, pitch

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
