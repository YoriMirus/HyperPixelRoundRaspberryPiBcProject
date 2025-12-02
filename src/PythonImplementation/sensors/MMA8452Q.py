from math import atan2, sqrt
import smbus2
import time


class MMA8452Q:
    # I2C slave addresses
    SLAVE_ADDR_HIGH = 0b0011101
    SLAVE_ADDR_LOW  = 0b0011100

    # Registers
    REG_CTRL1 = 0x2A
    REG_XYZ_DATA_CFG = 0x0E
    REG_OUT_X_MSB = 0x01

    REG_WHOAMI = 0x0D
    WHOAMI_EXPECTED = 0x2A  # MMA8452Q ID value

    def __init__(self, bus=11, address=SLAVE_ADDR_LOW, scale=2):
        """
        :param bus: I2C bus number (11 on Raspberry Pi)
        :param address: I²C address of sensor
        :param scale: ±2, ±4, ±8 g
        """
        self.bus = smbus2.SMBus(bus)
        self.address = address

        # Setup measurement scale
        if scale == 4:
            self.scale_bits = 0b01
            self.scale = 4
        elif scale == 8:
            self.scale_bits = 0b10
            self.scale = 8
        else:
            self.scale_bits = 0b00
            self.scale = 2  # default

        self.bufferX = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.bufferY = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.bufferZ = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.bufferIndex = 0

        # Initialize sensor
        self._enter_standby()
        self._configure_scale()
        self._enter_active()


    @staticmethod
    def detect(bus_number):
        """
        Returns True if an MMA8452Q sensor responds on the given bus.
        """
        try:
            bus = smbus2.SMBus(bus_number)
        except:
            return False

        for addr in (MMA8452Q.SLAVE_ADDR_LOW, MMA8452Q.SLAVE_ADDR_HIGH):
            try:
                whoami = bus.read_byte_data(addr, MMA8452Q.REG_WHOAMI)
                if whoami == MMA8452Q.WHOAMI_EXPECTED:
                    bus.close()
                    return addr  # return the working address!
            except:
                pass

        bus.close()
        return None

    # -------------------------------------------------------
    # Initialization and power control
    # -------------------------------------------------------

    def _read_register(self, reg):
        return self.bus.read_byte_data(self.address, reg)

    def _write_register(self, reg, value):
        self.bus.write_byte_data(self.address, reg, value)

    def _enter_standby(self):
        """Put sensor into standby (needed before reconfiguring)."""
        ctrl1 = self._read_register(self.REG_CTRL1)
        ctrl1 &= 0b11111110     # clear ACTIVE bit
        self._write_register(self.REG_CTRL1, ctrl1)

    def _enter_active(self):
        """Put sensor into active mode so it starts measuring."""
        ctrl1 = self._read_register(self.REG_CTRL1)
        ctrl1 |= 0b00000001     # set ACTIVE bit
        self._write_register(self.REG_CTRL1, ctrl1)

    def _configure_scale(self):
        """Write scale settings into XYZ_DATA_CFG register."""
        cfg = self._read_register(self.REG_XYZ_DATA_CFG)
        cfg &= 0b11111100       # Clear scale bits
        cfg |= self.scale_bits  # Insert the correct scale
        self._write_register(self.REG_XYZ_DATA_CFG, cfg)

    # -------------------------------------------------------
    # Reading sensor data
    # -------------------------------------------------------

    def read_raw_6bytes(self):
        """
        Reads the six OUT_X/Y/Z_MSB/LSB registers.
        """
        # Write the first register address, then read 6 bytes
        return self.bus.read_i2c_block_data(self.address, self.REG_OUT_X_MSB, 6)

    @staticmethod
    def _convert_msb_lsb(msb, lsb):
        """
        Convert 12-bit accelerometer output into signed short.

        MSB = upper 8 bits
        LSB = upper 4 bits of lower byte
        """
        # top 12 bits: MSB << 4  + upper 4 bits of LSB
        result = (msb << 4) | (lsb >> 4)

        # If the sign bit is set (MSB bit 7), extend sign
        if msb & 0x80:
            result |= 0xF000  # set upper 4 bits to 1

        return result if result < 32768 else result - 65536

    def read_acceleration(self):
        """
        Returns acceleration in g for each axis.
        :return: (ax, ay, az)
        """
        data = self.read_raw_6bytes()

        x_raw = self._convert_msb_lsb(data[0], data[1])
        y_raw = self._convert_msb_lsb(data[2], data[3])
        z_raw = self._convert_msb_lsb(data[4], data[5])

        # Counts per g from your C# code:
        counts_per_g = 1024.0 * 2 / self.scale

        ax = x_raw / counts_per_g
        ay = y_raw / counts_per_g
        az = z_raw / counts_per_g

        self.bufferX[self.bufferIndex] = ax
        self.bufferY[self.bufferIndex] = ay
        self.bufferZ[self.bufferIndex] = az
        self.bufferIndex += 1
        if self.bufferIndex >= len(self.bufferX):
            self.bufferIndex = 0

        ax = sum(self.bufferX) / len(self.bufferX)
        ay = sum(self.bufferY) / len(self.bufferY)
        az = sum(self.bufferZ) / len(self.bufferZ)

        return ax, ay, az

    def read_gyro(self):
        x,y,z = self.read_acceleration()

        roll = atan2(y, z) * 57.3
        pitch = atan2((-x), sqrt(y*y + z*z)) * 57.3

        return roll, (pitch * (-1))


    # -------------------------------------------------------
    # Cleanup
    # -------------------------------------------------------

    def close(self):
        """Turn sensor into standby mode and close bus."""
        if self.bus is None:
            return

        # Put device into standby
        ctrl1 = self._read_register(self.REG_CTRL1)
        ctrl1 &= 0b11111110
        self._write_register(self.REG_CTRL1, ctrl1)

        self.bus.close()
        self.bus = None

    def __del__(self):
        self.close()
