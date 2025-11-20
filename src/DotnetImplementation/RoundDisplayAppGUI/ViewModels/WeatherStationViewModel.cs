using System;
using Avalonia.Threading;
using CommunicationLibrary;
using CommunicationLibrary.I2CSensors.DTOs;

namespace RoundDisplayAppGUI.ViewModels;

public class WeatherStationViewModel : ViewModelBase
{
    public string TimeString
    {
        get => _TimeString;
        set => SetProperty(ref _TimeString, value);
    }
    private string _TimeString;

    public string DateString
    {
        get => _DateString;
        set =>  SetProperty(ref _DateString, value);
    }
    private string _DateString;

    public ISensorDataSource<HumidityTemperatureDTO>? Sensor
    {
        get => _Sensor;
        set
        {
            if (value is null)
                return;
            if (_Sensor is not null)
            {
                _Sensor.OnDataReceived -= SensorOnOnDataReceived;
                _Sensor.Dispose();
            }
            _Sensor = value;
            _Sensor.OnDataReceived += SensorOnOnDataReceived;
        }
    }
    private ISensorDataSource<HumidityTemperatureDTO>? _Sensor;


    public string TemperatureString
    {
        get => _TemperatureString;
        set => SetProperty(ref _TemperatureString, value);
    }
    private string _TemperatureString;

    public string HumidityString
    {
        get => _HumidityString;
        set => SetProperty(ref _HumidityString, value);
    }

    private string _HumidityString;

    private void SensorOnOnDataReceived(object sender, SensorDataEventArgs<HumidityTemperatureDTO> e)
    {
        Dispatcher.UIThread.Invoke(() =>
        {
            TemperatureString = e.Value.Temperature.ToString();
            HumidityString = e.Value.Humidity.ToString();
        });
    }

    public WeatherStationViewModel()
    {
        _TemperatureString = "21,0";
        _HumidityString = "70";
        _TimeString = "";
        _DateString = "";

        SetTime(DateTime.Now);
    }

    public void SetTime(DateTime time)
    {
        TimeString = time.ToString("HH:mm");

        string dayOfWeek = "";
        switch (time.DayOfWeek)
        {
            case DayOfWeek.Monday:
                dayOfWeek = "PO";
                break;
            case DayOfWeek.Tuesday:
                dayOfWeek = "ÚT";
                break;
            case DayOfWeek.Wednesday:
                dayOfWeek = "ST";
                break;
            case DayOfWeek.Thursday:
                dayOfWeek = "ČT";
                break;
            case DayOfWeek.Friday:
                dayOfWeek = "PÁ";
                break;
            case DayOfWeek.Saturday:
                dayOfWeek = "SO";
                break;
            case DayOfWeek.Sunday:
                dayOfWeek = "NE";
                break;
        }
        
        DateString = $"{dayOfWeek} {time:dd.MM.yy}";
    }
}