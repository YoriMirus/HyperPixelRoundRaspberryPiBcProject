using System;
using System.Device.I2c;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Interactivity;
using Avalonia.Markup.Xaml;
using Avalonia.Threading;
using Avalonia.VisualTree;
using Iot.Device.Board;
using Iot.Device.SenseHat;

namespace RoundDisplayAppGUI.Views;

public partial class SensorSettings : UserControl
{
    public SensorSettings()
    {
        InitializeComponent();
        if (App.IsRaspberryPi)
            InitializeRaspberryPi();
    }

    void InitializeRaspberryPi()
    {
        TemperatureHumiditySensorButton.IsEnabled = true;
        AccelerometerButton.IsEnabled = true;
    }
    

    private void AccelerometerButton_OnClick(object? sender, RoutedEventArgs e)
    {
        Visual? parent = this.GetVisualParent();
        while (parent is not null && parent is not MainWindow)
        {
            parent = parent?.GetVisualParent();
        }

        if (parent is MainWindow mw)
        {
            mw.ActivateAccelerometer();
        }
    }

    private void TemperatureHumiditySensorButton_OnClick(object? sender, RoutedEventArgs e)
    {
        Visual? parent = this.GetVisualParent();
        while (parent is not null && parent is not MainWindow)
        {
            parent = parent?.GetVisualParent();
        }

        if (parent is MainWindow mw)
        {
            mw.ActivateTemperatureHumiditySensor();
        }
    }
}