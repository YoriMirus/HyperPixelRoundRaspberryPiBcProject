import math
import random


class VirtualAccelerometer:
    def __init__(self, bus=11, address=None, scale=2):
        self.scale = scale

        # True orientation (fixed)
        self.true_roll = 0
        self.true_pitch = 0

        # Noise level (degrees, approx ± range)
        self.noise_std = 0  # ~99% within ±0.5°

    # -------------------------------------------------------
    # Core math
    # -------------------------------------------------------

    def _compute_acceleration(self, roll, pitch):
        r = math.radians(roll)
        p = math.radians(pitch)

        ax = -math.sin(p)
        ay = math.sin(r) * math.cos(p)
        az = math.cos(r) * math.cos(p)

        return ax, ay, az

    # -------------------------------------------------------
    # Noise model
    # -------------------------------------------------------

    def _noisy_angles(self):
        roll = self.true_roll + random.gauss(0, self.noise_std)
        pitch = self.true_pitch + random.gauss(0, self.noise_std)
        return roll, pitch

    # -------------------------------------------------------
    # API
    # -------------------------------------------------------

    def read_acceleration_raw(self):
        roll, pitch = self._noisy_angles()
        return self._compute_acceleration(roll, pitch)

    def read_acceleration(self):
        return self.read_acceleration_raw()

    def read_gyro(self):
        # Return noisy orientation as well
        return self._noisy_angles()

    # -------------------------------------------------------
    # Compatibility stubs
    # -------------------------------------------------------

    @staticmethod
    def detect(bus_number):
        return 0x1C

    def calibrate_level(self, *args, **kwargs):
        pass

    def close(self):
        pass