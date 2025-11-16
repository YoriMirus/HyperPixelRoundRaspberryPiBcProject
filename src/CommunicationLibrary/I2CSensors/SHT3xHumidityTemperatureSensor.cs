using CommunicationLibrary.I2CSensors.DTOs;

namespace CommunicationLibrary.I2CSensors;

using Iot.Device.Sht3x;
using System.Device.I2c;

public class SHT3xHumidityTemperatureSensor : ISensorDataSource<HumidityTemperatureDTO>
{
    private Sht3x? SHT3xDevice { get; set; }
    private I2cDevice? I2CDevice { get; set; }
    private int I2CBusNumber { get; }
    private int DurationBetweenReads { get; }
    
    public void Dispose()
    {
        SHT3xDevice?.Dispose();
        I2CDevice?.Dispose();
        SHT3xDevice = null;
        I2CDevice = null;
    }
    
    public event SensorDataReceivedHandler<HumidityTemperatureDTO>? OnDataReceived;
    public void StartListening()
    {
        if (SHT3xDevice is not null && I2CDevice is not null)
        {
            SHT3xDevice.Dispose();
            I2CDevice.Dispose();
        }

        var i2CSettings = new I2cConnectionSettings(I2CBusNumber, 0x45);
        I2CDevice = I2cDevice.Create(i2CSettings);
        SHT3xDevice = new Sht3x(I2CDevice);

        Task.Run(async () =>
        {
            try
            {
                await ReadingLoop();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"ReadingLoop exception: {ex.Message}");
            }
        });
    }

    public void StopListening()
    {
        Dispose();
    }
    
    private async Task ReadingLoop()
    {
        while (SHT3xDevice is not null && I2CDevice is not null)
        {
            var temp = SHT3xDevice.Temperature.DegreesCelsius;
            var humidity = SHT3xDevice.Humidity.Percent;
            
            OnDataReceived?.Invoke(this, new SensorDataEventArgs<HumidityTemperatureDTO>(DateTime.Now, new HumidityTemperatureDTO(humidity, temp)));
            
            await Task.Delay(DurationBetweenReads);
        }
    }

    public SHT3xHumidityTemperatureSensor(int i2CBusNumber, int durationBetweenReads)
    {
        I2CBusNumber = i2CBusNumber;
        DurationBetweenReads = durationBetweenReads;
    }
}