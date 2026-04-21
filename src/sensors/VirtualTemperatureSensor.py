import random


class VirtualTemperatureSensor:
    DEFAULT_I2C_ADDR = 0x45

    def __init__(self, bus=1, address=DEFAULT_I2C_ADDR):
        self.address = address
        self.bus = None

        # Base values
        self.base_temperature = 27.3
        self.base_humidity = 65.8

        # Noise limits
        self.temp_noise_range = 0.2   # ±0.2 °C
        self.hum_noise_range = 1.0    # ±1 %

    # -------------------------------------------------------
    # Noise helpers
    # -------------------------------------------------------

    def _bounded_gauss(self, mean, max_dev):
        """
        Gaussian noise clipped to ±max_dev
        """
        std = max_dev / 3  # ~99.7% inside bounds before clipping
        val = random.gauss(mean, std)

        return max(mean - max_dev, min(mean + max_dev, val))

    # -------------------------------------------------------
    # API
    # -------------------------------------------------------

    def read_measurement(self):
        temperature = self._bounded_gauss(self.base_temperature, self.temp_noise_range)
        humidity = self._bounded_gauss(self.base_humidity, self.hum_noise_range)

        return temperature, humidity

    def set_values(self, temperature, humidity):
        self.base_temperature = temperature
        self.base_humidity = humidity

    @staticmethod
    def detect(bus_number):
        return SHT3x.DEFAULT_I2C_ADDR