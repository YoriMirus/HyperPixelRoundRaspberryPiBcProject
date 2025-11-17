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
        /* OLD CODE HERE
        double y = e.Value.AccelerationY;
        double x = e.Value.AccelerationX;
        
        double angleRad = Math.Atan2(-y, x);
        double angleDeg = angleRad * (180.0 / Math.PI) + 90;

        Dispatcher.UIThread.Invoke(() =>
        {
            RotateTransform = new RotateTransform(angleDeg);
        });*/

        double x = e.Value.AccelerationX;
        double y = e.Value.AccelerationY;
        double z = e.Value.AccelerationZ;
        
        // 1. Normalize the accelerometer vector
        double len = Math.Sqrt(x * x + y * y + z * z);
        if (len < 1e-6) return; // avoid division by zero
        double gx = x / len;
        double gy = y / len;
        //double gz = z / len;

        // 2. Compute Euler angles (degrees) for Rotate3DTransform
        // Pitch (rotation around X-axis) — tilt forward/back
        double pitchRad = Math.Asin(-gx);
        double pitchDeg = pitchRad * 180.0 / Math.PI;

        // Roll (rotation around Y-axis) — tilt left/right
        double rollRad = Math.Asin(gy / Math.Cos(pitchRad));
        double rollDeg = rollRad * 180.0 / Math.PI;

        // Yaw (rotation around Z-axis) — leave 0 for now
        double yawDeg = 0;

        // 3. Apply rotation on the UI thread
        Dispatcher.UIThread.Invoke(() =>
        {
            RotateTransform = new Rotate3DTransform()
            {
                AngleX = pitchDeg,
                AngleY = rollDeg,
                AngleZ = yawDeg
            };
        });
    }
}