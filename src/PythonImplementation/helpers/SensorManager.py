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
            else:
                if SHT3x.detect(11):
                    self.SHT3x = SHT3x(bus=11)
            if self.MMA8452Q is not None:
                self.MMA8452Q.read_acceleration()
            else:
                if MMA8452Q.detect(11):
                    self.MMA8452Q = MMA8452Q(bus=11)
        except Exception as e:
            print(e)