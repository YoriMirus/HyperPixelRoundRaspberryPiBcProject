# brightness.py
import pigpio


class BrightnessController:
    PWM_PIN = 18
    PWM_RANGE = 255

    # Adjust after testing your specific unit
    MIN_PWM = 20      # ~8% hardware floor (visible but very dim)
    MAX_PWM = 255

    def __init__(self):
        self.pi = pigpio.pi()
        if not self.pi.connected:
            raise RuntimeError("pigpio daemon not running")

        self.pi.set_PWM_frequency(self.PWM_PIN, 1000)
        self.pi.set_PWM_range(self.PWM_PIN, self.PWM_RANGE)

    # ---------- Public API ----------

    def set_brightness_percent(self, percent: int):
        """
        0–100% where 0% is very dim (not off).
        """
        percent = max(0, min(100, percent))

        pwm_value = self._percent_to_pwm(percent)
        self.pi.set_PWM_dutycycle(self.PWM_PIN, pwm_value)

    def blackout(self):
        """
        Completely disable backlight.
        Use intentionally (sleep mode, shutdown, etc).
        """
        self.pi.set_PWM_dutycycle(self.PWM_PIN, 0)

    def restore_minimum(self):
        """
        Restore minimum visible brightness.
        """
        self.pi.set_PWM_dutycycle(self.PWM_PIN, self.MIN_PWM)

    def shutdown(self):
        self.blackout()
        self.pi.stop()

    # ---------- Internal Helpers ----------

    def _percent_to_pwm(self, percent: int) -> int:
        """
        Maps 0–100% into MIN_PWM–MAX_PWM
        """
        span = self.MAX_PWM - self.MIN_PWM
        return int(self.MIN_PWM + (percent / 100) * span)
