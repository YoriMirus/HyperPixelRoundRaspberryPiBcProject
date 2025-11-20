using Avalonia.Media;
using CommunicationLibrary;
using CommunicationLibrary.I2CSensors.DTOs;

using System;
using System.Numerics;
using Avalonia.Threading;

namespace RoundDisplayAppGUI.ViewModels;

public class GroundFinderViewModel : ViewModelBase
{
    public ISensorDataSource<AccelerometerDTO>? Sensor
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
    private ISensorDataSource<AccelerometerDTO>? _Sensor;

    public ITransform RotateTransform
    {
        get => _RotateTransform;
        set => SetProperty(ref _RotateTransform, value);
    }
    private ITransform _RotateTransform;

    public GroundFinderViewModel()
    {
        _RotateTransform = new RotateTransform(0);
    }
    
    private void SensorOnOnDataReceived(object sender, SensorDataEventArgs<AccelerometerDTO> e)
    {
        double y = e.Value.AccelerationY;
        double x = e.Value.AccelerationX;
        
        double angleRad = Math.Atan2(-y, x);
        double angleDeg = angleRad * (180.0 / Math.PI) + 90;

        Dispatcher.UIThread.Invoke(() =>
        {
            RotateTransform = new RotateTransform(angleDeg);
        });
    }
}