using System.Device.I2c;
using CommunicationLibrary.I2CSensors.DTOs;
using Iot.Device.Bmp180;

namespace CommunicationLibrary.I2CSensors;

public class Bmp180Gy68PressureTemperatureSensor : ISensorDataSource<PressureTemperatureAltitudeDTO>
{
    private Bmp180? Bmp180Device { get; set; }
    private I2cDevice? I2cDevice { get; set; }
    private int I2CBusNumber { get; }
    private int DurationBetweenReads { get; }
    public void Dispose()
    {
        Bmp180Device?.Dispose();
        I2cDevice?.Dispose();
        Bmp180Device = null;
        I2cDevice = null;
    }

    public event SensorDataReceivedHandler<PressureTemperatureAltitudeDTO>? OnDataReceived;
    public void StartListening()
    {
        if (Bmp180Device is not null && I2cDevice is not null)
        {
            Bmp180Device.Dispose();
            I2cDevice.Dispose();
        }

        var i2CSettings = new I2cConnectionSettings(I2CBusNumber, Bmp180.DefaultI2cAddress);
        I2cDevice = I2cDevice.Create(i2CSettings);
        Bmp180Device = new Bmp180(I2cDevice);
        
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

    public Bmp180Gy68PressureTemperatureSensor(int i2CBusNumber, int durationBetweenReads)
    {
        I2CBusNumber = i2CBusNumber;
        DurationBetweenReads = durationBetweenReads;
    }

    private async Task ReadingLoop()
    {
        while (Bmp180Device is not null && I2cDevice is not null)
        {
            var alt = Bmp180Device.ReadAltitude();
            var press =  Bmp180Device.ReadPressure();
            var temp = Bmp180Device.ReadTemperature();
            
            OnDataReceived?.Invoke(this, new SensorDataEventArgs<PressureTemperatureAltitudeDTO>(DateTime.Now, new PressureTemperatureAltitudeDTO(press.Atmospheres, temp.DegreesCelsius, alt.Meters)));
            
            await Task.Delay(DurationBetweenReads);
        }
    }
}