using System;
using Avalonia.Controls;
using Avalonia.Media;
using Avalonia.Threading;
using RoundDisplayAppGUI.ViewModels;

namespace RoundDisplayAppGUI.Views;

public partial class MainWindow : Window
{
    public MainWindow()
    {
        InitializeComponent();
        //DataContext = new MainWindowViewModel();

        DispatcherTimer.Run(OnTimerTick, TimeSpan.FromMilliseconds(100), DispatcherPriority.ApplicationIdle);
        
        this.SecondHandImage.RenderTransform = new RotateTransform()
        {
            Angle = 69,
            CenterX = 0.5,
            CenterY = 0.5
        };
    }

    bool OnTimerTick()
    {
        if (DataContext is null)
            return true;
        
        ((MainWindowViewModel)DataContext).SetSecondHand((byte)DateTime.Now.Second);
        
        // Časovač potřebuje vědět, zda má tuto metodu zavolat znova
        // Nemáme důvod to přerušovat, takže vždycky dáváme true, a.k.a. pokračovat časování
        return true;
    }
}