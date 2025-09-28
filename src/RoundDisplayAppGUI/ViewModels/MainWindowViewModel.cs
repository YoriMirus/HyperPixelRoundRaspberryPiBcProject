using System;

namespace RoundDisplayAppGUI.ViewModels;

using Avalonia.Media;
using Avalonia;
using CommunityToolkit.Mvvm.ComponentModel;

public partial class MainWindowViewModel : ViewModelBase
{
    public string Greeting { get; } = "Welcome to Avalonia!";

    public ITransform RotationTransform
    {
        get => _rotationTransform;
        set
        {
            _rotationTransform = value;
            this.OnPropertyChanged(nameof(RotationTransform));
        }
    }
    private ITransform _rotationTransform;

    public MainWindowViewModel()
    {
        RotationTransform = new RotateTransform()
        {
            Angle = 0, CenterX = 480 / 2,
            CenterY = 480 / 2
        };
    }
    
    public void SetSecondHand(byte seconds)
    {
        if (seconds > 60)
        {
            throw new ArgumentOutOfRangeException(nameof(seconds), seconds, "Seconds must have a value from 0 to 60.");
        }
        
        // 0 sekund je -90 stupňů.
        // 15 sekund je 0 stupňů
        // 30 sekund je 90 stupňů
        // 45 sekund je 180 stupňů
        // 60 sekund je -90 (270) stupňů

        int angle = (90/15) * seconds - 90;

        RotationTransform = new RotateTransform()
        {
            Angle = angle,
            CenterX = 0.5,
            CenterY = 0.5
        };
        
    }
}
