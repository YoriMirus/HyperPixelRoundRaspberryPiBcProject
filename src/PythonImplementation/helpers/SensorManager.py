from smbus2 import SMBus

from sensors.MMA8452Q import MMA8452Q
from sensors.SHT3x import SHT3x


class SensorManager:
    def __init__(self):
        self.SHT3x = None
        self.MMA8452Q = None

    def CheckForSensors(self):
        try:
            if self.SHT3x is not None:
                self.SHT3x.read_measurement()
            elif self.MMA8452Q is not None:
                self.MMA8452Q.read_acceleration()
            else:
                print("No sensor currently active. Attempting to connect...")

                try:
                    print("Looking for SHT3x...")
                    self.SHT3x = SHT3x(bus=11)
                except Exception as e:
                    print("Connecting to SHT3x failed.")
                    print(e)
                    print("Let's try the accelerometer.")

                try:
                    print("Looking for MMA8452Q...")
                    self.MMA8452Q = MMA8452Q(bus=11)
                except Exception as e:
                    print("Connecting to MMA8452Q failed. No sensors found.")
                    print(e)

            # Bud senzory fungují, nebo nejde se na senzor připojit. Řekněme MainWindow, ať pokračuje dál.
            return False

        except Exception as e:
            print("Something happened while checking sensors.")
            print(e)
            # Něco selhalo při čtení. Řekněme MainWindow ať to zkusí znovu.
            return True