using System;
using System.Threading;
using Avalonia.Controls;
using Avalonia.Input;
using Avalonia;
using Avalonia.Media;
using Avalonia.Styling;
using Avalonia.Animation;
using Avalonia.Animation.Easings;
using Avalonia.Threading;
using RoundDisplayAppGUI.ViewModels;

namespace RoundDisplayAppGUI.Views;

public partial class MainWindow : Window
{
    private Point _mousePressPosition;
    private bool _isPointerPressed;
    private Thickness originalMargin;
    
    public MainWindow()
    {
        InitializeComponent();
    }

    private void OnMousePressed(object? sender, PointerPressedEventArgs e)
    {
        _isPointerPressed = true;
        originalMargin = ContentGrid.Margin;
        _mousePressPosition = e.GetPosition(this);
        Console.WriteLine($"x: {e.GetPosition(this).X}, y: {e.GetPosition(this).Y}");
        e.Handled = true;
    }

    private async void OnMouseReleased(object? sender, PointerReleasedEventArgs e)
    {
        _isPointerPressed = false;
        Console.WriteLine($"x: {e.GetPosition(this).X}, y: {e.GetPosition(this).Y}");

        double deltaY = _mousePressPosition.Y - e.GetPosition(this).Y;

        Thickness newMargin = originalMargin;

        if (deltaY > 120)
        {
            newMargin = new Thickness(originalMargin.Left, originalMargin.Top - 960, originalMargin.Right,
                originalMargin.Bottom);
        }
        else if (deltaY < -120)
        {
            newMargin = new Thickness(originalMargin.Left, originalMargin.Top + 960, originalMargin.Right,
                originalMargin.Bottom);
        }

        originalMargin = newMargin;
        
        // Vytvořme animaci, aby ten přechod byl plynulý

        var anim = new Animation
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
                        new Setter(MarginProperty, ContentGrid.Margin)
                    }
                },
                new KeyFrame
                {
                    Cue = new Cue(1d),
                    Setters =
                    {
                        new Setter(MarginProperty, newMargin)
                    }
                }
            },
            // Forward = poté, co animace skončí, zůstane poslední hodnota zapsaná v marginu
            // Defaultně z nějakého divného důvodu animace vždy svůj účinek zruší
            FillMode = FillMode.Forward
        };
        
        // Run the animation on the grid
        await anim.RunAsync(ContentGrid, CancellationToken.None);
        //ContentGrid.Margin = newMargin;
        e.Handled = true;
    }

    private void OnMouseMoved(object? sender, PointerEventArgs e)
    {
        if (!_isPointerPressed)
            return;
        
        double deltaY = _mousePressPosition.Y - e.GetPosition(this).Y;
        ContentGrid.Margin = new Thickness(ContentGrid.Margin.Left, originalMargin.Top - (deltaY * 2),
            ContentGrid.Margin.Right, ContentGrid.Margin.Bottom);
        
        Console.WriteLine($"x: {e.GetPosition(this).X}, y: {e.GetPosition(this).Y}");
    }
}