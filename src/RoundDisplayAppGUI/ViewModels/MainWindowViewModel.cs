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
        set
        {
            _clockVM = value;
            OnPropertyChanged();
        }
    }

    private ClockViewModel _clockVM;
    
    public MainWindowViewModel()
    {
        ClockVM = new ClockViewModel();
        // Assignuju znova sama sebe, aby kompilátor ztichnul
        _clockVM = ClockVM;
    }
}
