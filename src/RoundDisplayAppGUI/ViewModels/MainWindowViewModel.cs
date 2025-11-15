using System;

namespace RoundDisplayAppGUI.ViewModels;

public partial class MainWindowViewModel : ViewModelBase
{
    /// <summary>
    /// Avalonia defaultně dává pro potomky datacontext rodiče. Musíme ho tedy ručně přepsat. Nejlépe pomocí vlastnosti v datacontextu rodiče.
    /// </summary>
    public ClockViewModel ClockVM
    {
        get => _clockVM;
        set => SetProperty(ref _clockVM, value);
    }
    private ClockViewModel _clockVM;

    public WeatherStationViewModel WeatherStationVM
    {
        get => _weatherVM;
        set => SetProperty(ref _weatherVM, value);
    }
    private WeatherStationViewModel _weatherVM;
    
    public MainWindowViewModel()
    {
        ClockVM = new ClockViewModel();
        WeatherStationVM = new WeatherStationViewModel();
        
        // Assignuju znova sama sebe, aby kompilátor ztichnul
        _weatherVM = WeatherStationVM;
        _clockVM = ClockVM;
    }
}
