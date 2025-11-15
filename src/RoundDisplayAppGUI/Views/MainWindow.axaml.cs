using System;
using System.Threading;
using Avalonia.Controls;
using Avalonia.Input;
using Avalonia;
using Avalonia.Styling;
using Avalonia.Animation;
using Avalonia.Animation.Easings;
using CommunicationLibrary.I2CSensors;
using RoundDisplayAppGUI.ViewModels;

namespace RoundDisplayAppGUI.Views;

public partial class MainWindow : Window
{
    private Point _mousePressPosition;
    private bool _isPointerPressed;
    private double _originalScroll;

    private bool currentlyScrolling;
    
    public MainWindow()
    {
        this.Closing += OnClosing;
        InitializeComponent();
        string hostName = Environment.MachineName;
        string userName =  Environment.UserName;

        Console.WriteLine("Host name: " + hostName);
        Console.WriteLine("User name: " + userName);

        if (hostName.Contains("raspberry") || hostName.Contains("rpi") || userName.Contains("raspberry") || userName.Contains("rpi"))
        {
            WindowState = WindowState.FullScreen;
            if (ClockWidget.DataContext is not WeatherStationViewModel vm)
                return;
            var sensor = new SHT3xHumidityTemperatureSensor(11, 100);
            
            vm.Sensor = sensor;
            sensor.StartListening();
        }
    }

    private void OnClosing(object? sender, WindowClosingEventArgs e)
    {
        ClockWidget.OnWindowClosing();
        WeatherStationWidget.OnWindowClosing();
    }

    private void OnMousePressed(object? sender, PointerPressedEventArgs e)
    {
        Console.WriteLine($"Mouse pressed ({e.Pointer.Id})");
        if (currentlyScrolling)
            return;
        Console.WriteLine($"Handling ({e.Pointer.Id})");
        
        _isPointerPressed = true;
        _originalScroll = MainContentScroller.Offset.Y;
        _mousePressPosition = e.GetPosition(this);
    }

    private async void OnMouseReleased(object? sender, PointerReleasedEventArgs e)
    {
        Console.WriteLine($"Mouse released {e.Pointer.Id}");
        if (currentlyScrolling)
            return;
        Console.WriteLine($"Handling ({e.Pointer.Id})");
        
        _isPointerPressed = false;

        double deltaY = _mousePressPosition.Y - e.GetPosition(this).Y;

        double newScroll = _originalScroll;

        if (deltaY < -120)
        {
            newScroll = _originalScroll - 480;
        }
        else if (deltaY > 120)
        {
            newScroll = _originalScroll + 480;
        }

        _originalScroll = newScroll;

        currentlyScrolling = true;
        
        // Vytvořme animaci, aby ten přechod byl plynulý
        var anim = CreateScrollAnimationTemplate(MainContentScroller.Offset, new Vector(MainContentScroller.Offset.X, newScroll));
        await anim.RunAsync(MainContentScroller, CancellationToken.None);

        currentlyScrolling = false;
    }

    private void OnMouseMoved(object? sender, PointerEventArgs e)
    {
        Console.WriteLine($"Mouse moved ({e.Pointer.Id})");
        if (!_isPointerPressed || currentlyScrolling)
            return;
        Console.WriteLine($"Handling ({e.Pointer.Id})");
        
        double deltaY = _mousePressPosition.Y - e.GetPosition(this).Y;
        MainContentScroller.Offset = new Vector(MainContentScroller.Offset.X, _originalScroll + (deltaY));
    }

    private void InputElement_OnPointerWheelChanged(object? sender, PointerWheelEventArgs e)
    {
        // Musíme zahodit mouse wheel event, je to udělané pro displej after all
        // Důvod proč to zakazuju je protože je to bolest implementovat společně s gestama, aniž by vznikly bugy
        e.Handled = true;
    }

    private Animation CreateScrollAnimationTemplate(Vector oldOffset, Vector newOffset)
    {
        return new Animation
        {
            Duration = TimeSpan.FromMilliseconds(300),
            Easing = new CubicEaseOut(), // nice smooth deceleration
            Children =
            {
                new KeyFrame
                {
                    Cue = new Cue(0d),
                    Setters =
                    {
                        new Setter(ScrollViewer.OffsetProperty, oldOffset)
                    }
                },
                new KeyFrame
                {
                    Cue = new Cue(1d),
                    Setters =
                    {
                        new Setter(ScrollViewer.OffsetProperty, newOffset)
                    }
                }
            },
            // Forward = poté, co animace skončí, zůstane poslední hodnota zapsaná v marginu
            // Defaultně z nějakého divného důvodu animace vždy svůj účinek zruší
            FillMode = FillMode.Forward
        };
    }
}