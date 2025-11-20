using CommunicationLibrary.I2CSensors.DTOs;

namespace CommunicationLibrary.I2CSensors;

using Iot.Device.Sht3x;
using System.Device.I2c;

public class SHT3xHumidityTemperatureSensor : SensorBase<HumidityTemperatureDTO, Sht3x>
{
    protected override void InitialiseSensorImplementation(I2cDevice device)
    {
        SensorImplementation = new Sht3x(device);
    }

    protected override HumidityTemperatureDTO ReadSensorData()
    {
        if (SensorImplementation is null)
            return new HumidityTemperatureDTO();
        
        var temp = SensorImplementation.Temperature.DegreesCelsius;
        var humidity = SensorImplementation.Humidity.Percent;
        
        return new HumidityTemperatureDTO(humidity, temp);
    }


    public SHT3xHumidityTemperatureSensor(int i2CBusNumber, TimeSpan durationBetweenReads) : base(i2CBusNumber, 0x45, durationBetweenReads)
    {
    }
}