using System.Device.I2c;

namespace CommunicationLibrary.I2CSensors;

public abstract class SensorBase<T, U> : ISensorDataSource<T> where U : IDisposable
{
    private readonly int _busNumber;
    private readonly int _sensorAddress;
    private readonly TimeSpan _durationBetweenReads;
    
    protected I2cDevice? I2CDevice;
    /// <summary>
    /// Dodatečná implementace senzoru, pokud se používá externí knihovna (SHT3x, Bmp180, atd.)
    /// Pokud pro implementaci není používána externí knihovna, nechej null.
    /// </summary>
    protected U? SensorImplementation;

    public void Dispose()
    {
        OnSensorDisposing();
        I2CDevice?.Dispose();
        I2CDevice = null;
    }

    public event SensorDataReceivedHandler<T>? OnDataReceived;
    public void StartListening()
    {
        if (I2CDevice is not null)
        {
            SensorImplementation?.Dispose();
            I2CDevice.Dispose();
        }
        
        var i2CSettings = new I2cConnectionSettings(_busNumber, _sensorAddress);
        I2CDevice = I2cDevice.Create(i2CSettings);
        InitialiseSensorImplementation(I2CDevice);
        
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

    private async Task ReadingLoop()
    {
        while (I2CDevice is not null)
        {
            T data = ReadSensorData();
            OnDataReceived?.Invoke(this, new SensorDataEventArgs<T>(DateTime.Now,data));
            
            await Task.Delay(_durationBetweenReads);
        }
    }

    public void StopListening()
    {
        Dispose();
    }

    /// <summary>
    /// Inicializuj implementaci senzoru. Pokud používáte externí knihovnu tak ji dosaďte do SensorBase.sensorImplementation. Pokud máte svou vlastní implementaci, zde nakonfigurujte zařízení.
    /// </summary>
    protected abstract void InitialiseSensorImplementation(I2cDevice device);

    /// <summary>
    /// Metoda, která se zavolá když je zavolána funkce Dispose. Pokud používáte externí knihovnu, nemusíte ji overridenout, SensorBase.sensorImplementation je zde disposenut. Pokud máte svou vlastní implementaci, zde resetujte registry, pokud je to nutné.
    /// </summary>
    protected virtual void OnSensorDisposing()
    {
        SensorImplementation?.Dispose();
        SensorImplementation = default;
    }

    protected abstract T ReadSensorData();
    
    protected SensorBase(int busNumber, int sensorAddress,TimeSpan durationBetweenReads)
    {
        _busNumber = busNumber;
        _sensorAddress = sensorAddress;
        _durationBetweenReads = durationBetweenReads;
    }
}