import random

from sensors.SHT3x import SHT3x


class VirtualTemperatureSensor:
    DEFAULT_I2C_ADDR = 0x45

    def __init__(self, bus=1, address=DEFAULT_I2C_ADDR):
        self.address = address
        self.bus = None

        # Base + target
        self.base_temperature = 30.0
        self.target_temperature = 30.0

        self.base_humidity = 65.8

        # Noise
        self.temp_noise_range = 2
        self.hum_noise_range = 3

        # Drift behavior
        self.alpha = 0.02          # smoothing speed
        self.change_prob = 0.01   # 0.1% chance

    # -------------------------------------------------------
    # Noise helpers
    # -------------------------------------------------------

    def _bounded_gauss(self, mean, max_dev):
        std = max_dev / 3
        val = random.gauss(mean, std)
        return max(mean - max_dev, min(mean + max_dev, val))

    # -------------------------------------------------------
    # API
    # -------------------------------------------------------

    def read_measurement(self):
        # --- occasionally pick new target ---
        if random.random() < self.change_prob:
            self.target_temperature = random.uniform(10, 30)

        # --- smooth drift toward target ---
        self.base_temperature += self.alpha * (self.target_temperature - self.base_temperature)

        # --- add noise ---
        temperature = self._bounded_gauss(self.base_temperature, self.temp_noise_range)
        humidity = self._bounded_gauss(self.base_humidity, self.hum_noise_range)

        return temperature, humidity

    def set_values(self, temperature, humidity):
        self.base_temperature = temperature
        self.target_temperature = temperature
        self.base_humidity = humidity

    @staticmethod
    def detect(bus_number):
        return SHT3x.DEFAULT_I2C_ADDR