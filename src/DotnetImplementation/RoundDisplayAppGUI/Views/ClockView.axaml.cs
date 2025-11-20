using Avalonia;
using Avalonia.Controls;
using Avalonia.Threading;
using Avalonia.Markup.Xaml;

using RoundDisplayAppGUI.ViewModels;


using System;

namespace RoundDisplayAppGUI.Views;



public partial class ClockView : UserControl
{
    private IDisposable _timer;
    
    public ClockView()
    {
        InitializeComponent();
        
        _timer = DispatcherTimer.Run(OnTimerTick, TimeSpan.FromMilliseconds(100), DispatcherPriority.ApplicationIdle);
    }

    public void OnWindowClosing()
    {
        // Timer je třeba zrušit během zavírání okna, protože se může dispatcher spustit po Disposenutí okna, což způsobí výjimku
        // Tato výjimka se sice stává při vypínání programu, takže to asi nic moc neovlivní, ale nevypadá to dobře mít v konzoli výjimky
        _timer.Dispose();
    }
    
    bool OnTimerTick()
    {
        if (DataContext is not ClockViewModel viewModel)
            return true;
        
        viewModel.SetTime(DateTime.Now);
        
        // Časovač potřebuje vědět, zda má tuto metodu zavolat znova
        // Nemáme důvod to přerušovat, takže vždycky dáváme true, a.k.a. pokračovat časování
        return true;
    }
}