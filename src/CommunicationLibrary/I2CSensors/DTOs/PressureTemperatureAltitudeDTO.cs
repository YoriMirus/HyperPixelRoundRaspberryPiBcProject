namespace CommunicationLibrary.I2CSensors.DTOs;

public struct PressureTemperatureAltitudeDTO
{
    /// <summary>
    /// Tlak v násobku atmosféry (atm)
    /// </summary>
    public double Pressure;

    /// <summary>
    /// Teplota v °C
    /// </summary>
    public double Temperature;

    /// <summary>
    /// Nadmořská výška v metrech
    /// </summary>
    public double Altitude;

    public PressureTemperatureAltitudeDTO(double pressure, double temperature, double altitude)
    {
        Pressure = pressure;
        Temperature = temperature;
        Altitude = altitude;
    }
}