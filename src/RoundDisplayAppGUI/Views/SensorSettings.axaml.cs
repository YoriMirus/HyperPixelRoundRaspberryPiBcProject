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
    private I2cBus? bus;
    public SensorSettings()
    {
        InitializeComponent();
        if (App.IsRaspberryPi)
            InitializeRaspberryPi();
    }

    void InitializeRaspberryPi()
    {
        bus = I2cBus.Create(11);
        DispatcherTimer.Run(CheckI2CBus, TimeSpan.FromMilliseconds(1000), DispatcherPriority.Background);
    }

    bool CheckI2CBus()
    {
        if (bus is null)
            return false;

        TemperatureHumiditySensorButton.IsEnabled = false;
        AccelerometerButton.IsEnabled = false;
        
        var devices = bus.PerformBusScan();
        foreach (int device in devices)
        {
            // 0x15 je odkaz na samotný displej.
            // c# by teoreticky toto zařízení vidět ani neměl, ale pro jistotu to sem dám.
            if (device == 0x15)
                continue;
            
            // SHT3x senzor vlhkosti a teploty
            if (device == 0x45)
            {
                TemperatureHumiditySensorButton.IsEnabled = true;
            }
            // Akcelerometr
            else if (device == 0x1C)
            {
                AccelerometerButton.IsEnabled = true;
            }
            else
            {
                Console.WriteLine($"Found an unrecognized sensor on address {device}.");
            }
        }
        
        return true;
    }

    private void AccelerometerButton_OnClick(object? sender, RoutedEventArgs e)
    {
        
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