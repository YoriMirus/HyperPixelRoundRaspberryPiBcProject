using Avalonia;
using Avalonia.Controls;
using Avalonia.Threading;
using Avalonia.Markup.Xaml;

using System;

namespace RoundDisplayAppGUI.Views;

using RoundDisplayAppGUI.ViewModels;

using CommunicationLibrary;


public partial class ClockView : UserControl
{
    
    public ClockView()
    {
        //this.DataContextChanged += InitializeDataContext;
        InitializeComponent();
        
        DispatcherTimer.Run(OnTimerTick, TimeSpan.FromMilliseconds(100), DispatcherPriority.ApplicationIdle);
    }
    
    bool OnTimerTick()
    {
        if (DataContext is null)
            return true;
        
        ((ClockViewModel)DataContext).SetTime(DateTime.Now);
        
        // Časovač potřebuje vědět, zda má tuto metodu zavolat znova
        // Nemáme důvod to přerušovat, takže vždycky dáváme true, a.k.a. pokračovat časování
        return true;
    }
}