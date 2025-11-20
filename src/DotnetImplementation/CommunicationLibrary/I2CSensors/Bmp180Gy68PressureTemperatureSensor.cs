using System.Device.I2c;
using CommunicationLibrary.I2CSensors.DTOs;
using Iot.Device.Bmp180;

namespace CommunicationLibrary.I2CSensors;

public class Bmp180Gy68PressureTemperatureSensor : SensorBase<PressureTemperatureAltitudeDTO, Bmp180>
{
    public Bmp180Gy68PressureTemperatureSensor(int i2CBusNumber, TimeSpan durationBetweenReads) : base(i2CBusNumber, Bmp180.DefaultI2cAddress, durationBetweenReads)
    {
    }

    protected override void InitialiseSensorImplementation(I2cDevice device)
    {
        SensorImplementation = new Bmp180(device);
    }

    protected override PressureTemperatureAltitudeDTO ReadSensorData()
    {
        if (SensorImplementation is null)
            return new PressureTemperatureAltitudeDTO();
        
        var press =  SensorImplementation.ReadPressure();
        var temp = SensorImplementation.ReadTemperature();
        var alt = SensorImplementation.ReadAltitude();

        return new PressureTemperatureAltitudeDTO(press.Atmospheres, temp.DegreesCelsius, alt.Meters);
    }
}