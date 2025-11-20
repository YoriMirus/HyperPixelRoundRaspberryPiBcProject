namespace CommunicationLibrary.I2CSensors.DTOs;

/// <summary>
/// Reprezentuje výsledek měření senzoru teploty a vlhkosti
/// </summary>
public struct HumidityTemperatureDTO
{
    /// <summary>
    /// Vlhkost v procentech (99% = 99.0)
    /// </summary>
    public double Humidity;
    /// <summary>
    /// Teplota ve stupních °C
    /// </summary>
    public double Temperature;

    public HumidityTemperatureDTO(double humidity, double temperature)
    {
        Humidity = humidity;
        Temperature = temperature;
    }
}