namespace CommunicationLibrary;

/// <summary>
/// Umožňuje posílání dat ze senzoru jinému zařízení, nezávisle na metodě komunikace
/// </summary>
public interface ISensorDataServer<T> : IDisposable
{
    /// <summary>
    /// Začne posílat data druhé straně (asynchronně na jiném vlákně)
    /// </summary>
    void Start();
    /// <summary>
    /// Přestane posílat data druhé straně
    /// </summary>
    void Stop();
    /// <summary>
    /// Změní data, které jsou posílané druhé straně.
    /// </summary>
    /// <param name="value">Nová hodnota</param>
    void UpdateValue(T value);
}