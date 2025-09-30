using System;
using System.ComponentModel;
using Avalonia.Controls;
using Avalonia.Media;
using Avalonia.Threading;
using RoundDisplayAppGUI.ViewModels;

namespace RoundDisplayAppGUI.Views;

public partial class MainWindow : Window
{
    private bool _continueTimer = true;
    
    public MainWindow()
    {
        Closing += OnWindowClosing;
        InitializeComponent();
        //DataContext = new MainWindowViewModel();

        DispatcherTimer.Run(OnTimerTick, TimeSpan.FromMilliseconds(100), DispatcherPriority.ApplicationIdle);
    }

    void OnWindowClosing(object? sender, CancelEventArgs e)
    {
        _continueTimer = false;
    }

    bool OnTimerTick()
    {
        if (DataContext is null)
            return true;
        
        ((MainWindowViewModel)DataContext).SetTime(DateTime.Now);
        
        // Časovač potřebuje vědět, zda má tuto metodu zavolat znova
        // Nemáme důvod to přerušovat, takže vždycky dáváme true, a.k.a. pokračovat časování
        return _continueTimer;
    }
}