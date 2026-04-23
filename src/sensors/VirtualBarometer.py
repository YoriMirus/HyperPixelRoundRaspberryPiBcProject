import math
import random


class VirtualBarometer:
    DEFAULT_PRESSURE = 101325  # Pa

    def __init__(self, bus=11, address=0x77):
        # keep API compatibility
        self.address = address
        self.bus = None

        # base values
        self.temperature = 22.5
        self.pressure = 101325.0
        self.altitude = 0.0

        self.sea_level_pressure = 101325.0

        # noise
        self.temp_noise = 0.1
        self.pressure_noise = 100

    # -------------------------------------------------------
    # Core physics
    # -------------------------------------------------------

    def _pressure_to_altitude(self, pressure):
        return 44330.0 * (1.0 - (pressure / self.sea_level_pressure) ** 0.1903)

    def _altitude_to_pressure(self, altitude):
        return self.sea_level_pressure * (1.0 - altitude / 44330.0) ** (1 / 0.1903)

    # -------------------------------------------------------
    # Setters (this is what you wanted)
    # -------------------------------------------------------

    def set_pressure(self, pressure):
        self.pressure = pressure
        self.altitude = self._pressure_to_altitude(pressure)

    def set_altitude(self, altitude):
        self.altitude = altitude
        self.pressure = self._altitude_to_pressure(altitude)

    def set_temperature(self, temperature):
        self.temperature = temperature

    # -------------------------------------------------------
    # Sensor reads (with noise)
    # -------------------------------------------------------

    def get_temp(self):
        return self.temperature + random.uniform(-self.temp_noise, self.temp_noise)

    def get_pressure(self):
        return self.pressure + random.uniform(-self.pressure_noise, self.pressure_noise)

    def get_altitude(self):
        # derive from current pressure for consistency
        return self._pressure_to_altitude(self.get_pressure())

    def read_measurement(self):
        return self.get_temp(), self.get_pressure(), self.get_altitude()

    # -------------------------------------------------------
    # Detection (fake success)
    # -------------------------------------------------------

    @staticmethod
    def detect(bus_number):
        return 0x77