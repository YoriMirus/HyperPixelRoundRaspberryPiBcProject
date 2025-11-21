import smbus2
import time

class SHT3x:
    DEFAULT_I2C_ADDR = 0x44

    # Commands
    CMD_MEASURE_HIGHREP_STRETCH = [0x2C, 0x06]   # High repeatability, clock stretching
    CMD_MEASURE_HIGHREP = [0x24, 0x00]           # No clock stretching

    def __init__(self, bus=1, address=DEFAULT_I2C_ADDR):
        self.address = address
        self.bus = smbus2.SMBus(bus)

    # CRC polynomial and helper from Sensirion datasheet
    @staticmethod
    def _crc8(data):
        polynomial = 0x31
        crc = 0xFF
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x80:
                    crc = (crc << 1) ^ polynomial
                else:
                    crc <<= 1
                crc &= 0xFF
        return crc

    def read_measurement(self):
        """Read both temperature and humidity from the SHT3x."""

        # Start a measurement (with stretching)
        self.bus.write_i2c_block_data(self.address, self.CMD_MEASURE_HIGHREP_STRETCH[0],
                                      [self.CMD_MEASURE_HIGHREP_STRETCH[1]])

        # Max measurement time is 15 ms
        time.sleep(0.02)

        # Read 6 bytes: T[2], T_CRC[1], RH[2], RH_CRC[1]
        data = self.bus.read_i2c_block_data(self.address, 0x00, 6)

        temp_raw = data[0:2]
        temp_crc = data[2]
        hum_raw = data[3:5]
        hum_crc = data[5]

        # Validate CRC
        if self._crc8(temp_raw) != temp_crc:
            raise ValueError("Temperature CRC mismatch")
        if self._crc8(hum_raw) != hum_crc:
            raise ValueError("Humidity CRC mismatch")

        # Convert raw values
        raw_t = temp_raw[0] << 8 | temp_raw[1]
        raw_h = hum_raw[0] << 8 | hum_raw[1]

        temperature = -45 + (175 * raw_t / 65535.0)
        humidity = 100 * raw_h / 65535.0

        return temperature, humidity

    def read_temperature(self):
        """Return °C as float."""
        return self.read_measurement()[0]

    def read_humidity(self):
        """Return % as float."""
        return self.read_measurement()[1]

    @staticmethod
    def detect(bus_number):
        """
        Returns True if a SHT3x sensor responds on the given bus.
        Checks addresses 0x44 and 0x45 (both are used in different modules).
        """
        possible_addresses = [0x44, 0x45]

        try:
            bus = smbus2.SMBus(bus_number)
        except:
            return None

        for addr in possible_addresses:
            try:
                # Soft measurement command (does not require CRC)
                bus.write_i2c_block_data(addr, 0x2C, [0x06])
                time.sleep(0.01)

                # Try reading data — if it works, sensor is present
                bus.read_i2c_block_data(addr, 0x00, 6)
                bus.close()
                return addr
            except:
                pass

        bus.close()
        return None
