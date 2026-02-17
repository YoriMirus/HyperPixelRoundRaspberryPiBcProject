from smbus2 import SMBus

from sensors.MMA8452Q import MMA8452Q
from sensors.SHT3x import SHT3x

from dataclasses import asdict

from networking.GetStatusDTO import *


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
                    self.MMA8452Q.calibrate_level()
        except Exception as e:
            print(e)

    def get_sensor_status(self, is_raspberry_pi: bool = False) -> GetStatusDTO:
        # --- SHT3x ---
        if self.SHT3x is not None:
            meas = self.SHT3x.read_measurement()
            sht3x_status = SHT3x(
                connected=True,
                values=TempData(
                    temperature=meas.temperature,
                    humidity=meas.humidity
                )
            )
        else:
            sht3x_status = SHT3x(
                connected=False,
                values=None
            )

        # --- MMA5452Q ---
        if self.MMA8452Q is not None:
            accel = self.MMA8452Q.read_acceleration()
            gyro = self.MMA8452Q.read_gyro()

            mma_status = MMA5452Q(
                connected=True,
                values_accel=AccelData(
                    x=accel.x,
                    y=accel.y,
                    z=accel.z
                ),
                values_gyro=GyroData(
                    roll=gyro.roll,
                    pitch=gyro.pitch
                )
            )
        else:
            mma_status = MMA5452Q(
                connected=False,
                values_accel=None,
                values_gyro=None
            )

        return GetStatusDTO(
            SHT3x=sht3x_status,
            MMA5452Q=mma_status,
            is_raspberry_pi=is_raspberry_pi
        )