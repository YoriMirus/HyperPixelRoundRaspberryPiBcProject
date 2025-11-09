using System.Device.I2c;
using Iot.Device.Bmp180;

namespace CommunicationLibrary.I2CSensors;

public class Bmp180Gy68PressureTemperatureSensor : ISensorDataSource<Tuple<double,double,double>>
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

    public event SensorDataReceivedHandler<Tuple<double, double,double>>? OnDataReceived;
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
            
            OnDataReceived?.Invoke(this, new SensorDataEventArgs<Tuple<double, double,double>>(DateTime.Now, new Tuple<double,double,double>(alt.Meters, press.Atmospheres, temp.DegreesCelsius)));
            
            await Task.Delay(DurationBetweenReads);
        }
    }
}