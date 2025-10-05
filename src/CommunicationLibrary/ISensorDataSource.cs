namespace CommunicationLibrary;


/// <summary>
/// Obsahuje data nasbírané ze senzoru
/// </summary>
/// <typeparam name="T"></typeparam>
public class SensorDataEventArgs<T> : EventArgs
{
    /// <summary>
    /// Kdy byly data detekovány
    /// </summary>
    public DateTime Timestamp { get; }
    /// <summary>
    /// Naměřená hodnota
    /// </summary>
    public T Value { get; }

    public SensorDataEventArgs(DateTime timestamp, T value)
    {
        Timestamp = timestamp;
        Value = value;
    }
}

public delegate void SensorDataReceivedHandler<T>(object sender, SensorDataEventArgs<T> e);

/// <summary>
/// Poskytuje zdroj dat ze snímače, nezávisle na způsobu sběru
/// </summary>
public interface ISensorDataSource<T> : IDisposable
{
    /// <summary>
    /// Tento event se spustí, když jsou přijaty nové data z komunikace
    /// </summary>
    public event  SensorDataReceivedHandler<T> OnDataReceived;
    /// <summary>
    /// Začne sbírat data
    /// </summary>
    public void StartListening();
    /// <summary>
    /// Přestane sbírat data
    /// </summary>
    public void StopListening();
}