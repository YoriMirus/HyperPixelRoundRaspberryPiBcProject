using System;

namespace RoundDisplayAppGUI.ViewModels;

using Avalonia.Media;
using Avalonia;
using CommunityToolkit.Mvvm.ComponentModel;

public partial class MainWindowViewModel : ViewModelBase
{
    public ITransform SecondHandRotation
    {
        get => _secondHandRotation;
        set
        {
            _secondHandRotation = value;
            OnPropertyChanged();
        }
    }
    private ITransform _secondHandRotation;

    public ITransform MinuteHandRotation
    {
        get => _minuteHandRotation;
        set
        {
            _minuteHandRotation = value;
            OnPropertyChanged();
        }
    }
    private ITransform _minuteHandRotation;

    public ITransform HourHandRotation
    {
        get => _hourHandRotation;
        set
        {
            _hourHandRotation = value;
            OnPropertyChanged();
        }
    }
    private ITransform _hourHandRotation;

    public string DayOfWeek
    {
        get => _dayOfWeek;
        set
        {
            _dayOfWeek = value;
            OnPropertyChanged();
        }
    }

    private string _dayOfWeek;

    public string DateStr
    {
        get => _dateStr;
        set
        {
            _dateStr = value;
            OnPropertyChanged();
        }
    }
    private string _dateStr;

    public MainWindowViewModel()
    {
        // Jako výchozí hodnotu natočení obrázku dáme 0°, což znamená, že obrázek není otočen
        
        SecondHandRotation = new RotateTransform()
        {
            Angle = 0,
            CenterX = 0.5,
            CenterY = 0.5
        };

        MinuteHandRotation = new RotateTransform()
        {
            Angle = 0,
            CenterX = 0.5,
            CenterY = 0.5
        };

        HourHandRotation = new RotateTransform()
        {
            Angle = 0,
            CenterX = 0.5,
            CenterY = 0.5
        };
        
        // Dosadíme do RT sama sebe, aby kompilátor nenadával
        // Kompilátor tohle stejně asi během kompilace smaže
        _secondHandRotation = SecondHandRotation;
        _minuteHandRotation = MinuteHandRotation;
        _hourHandRotation = HourHandRotation;

        _dateStr = string.Empty;
        _dayOfWeek = string.Empty;
    }

    public void SetTime(DateTime time)
    {
        SetSecondHand(time.Second);
        SetMinuteHand(time.Minute + ((double)time.Second / 60));
        SetHourHand(time.Hour + ((double)time.Minute / 60));

        switch (time.DayOfWeek)
        {
            case System.DayOfWeek.Monday:
                DayOfWeek = "PO";
                break;
            case System.DayOfWeek.Tuesday:
                DayOfWeek = "ÚT";
                break;
            case System.DayOfWeek.Wednesday:
                DayOfWeek = "ST";
                break;
            case System.DayOfWeek.Thursday:
                DayOfWeek = "ČT";
                break;
            case System.DayOfWeek.Friday:
                DayOfWeek = "PÁ";
                break;
            case System.DayOfWeek.Saturday:
                DayOfWeek = "SO";
                break;
            case System.DayOfWeek.Sunday:
                DayOfWeek = "NE";
                break;
        }

        DateStr = time.ToString("dd.MM.yyyy");
    }
    
    private void SetSecondHand(int seconds)
    {
        // 0 sekund je -90 stupňů.
        // 15 sekund je 0 stupňů
        // 30 sekund je 90 stupňů
        // 45 sekund je 180 stupňů
        // 60 sekund je -90 (270) stupňů

        int angle = (90/15) * seconds - 90;

        SecondHandRotation = new RotateTransform()
        {
            Angle = angle,
            CenterX = 0.5,
            CenterY = 0.5
        };
    }

    private void SetMinuteHand(double minutes)
    {
        // Princip stejný jako u sekundové ručičky, jenom už je přesnější
        // Ručičku ale posouvám o 2.5 stupňů zpátky kvůli nepřesnostem způsobeným mou úpravou obrázků
        double angle = (90.0 / 15) * minutes - 90 - 2.5;

        MinuteHandRotation = new RotateTransform()
        {
            Angle = angle,
            CenterX = 0.5,
            CenterY = 0.5
        };
    }
    
    private void SetHourHand(double hours)
    {
        // 0 hodin = -90 stupňů
        // 3 hodiny = 0 stupňů
        // 6 hodin = 90 stupňů
        // 9 hodin = 180 stupňů
        // 12 hodin = 270 stupňů (-90)
        
        double angle = (90 / 3) * hours - 90;

        HourHandRotation = new RotateTransform()
        {
            Angle = angle,
            CenterX = 0.5,
            CenterY = 0.5
        };
    }
}
