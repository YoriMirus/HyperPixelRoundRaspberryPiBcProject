using System;
using System.Globalization;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Markup.Xaml;
using Avalonia.Media;
using Avalonia.Threading;
using CommunicationLibrary;
using RoundDisplayAppGUI.Helpers;

namespace RoundDisplayAppGUI.Views;

public partial class Speedometer : UserControl
{
    public static ISensorDataSource<double>? SpeedometerDataSource
    {
        get
        {
            return _speedoDataSource;
        }
        set
        {
            _speedoDataSource = value;
            DataSourceChanged?.Invoke(null, EventArgs.Empty);
        }
    }
    private static ISensorDataSource<double>? _speedoDataSource;
    private static event EventHandler? DataSourceChanged;

    private double _currentValue = 25.0;
    
    // Parametry
    readonly double _startAngle = 135 * Math.PI / 180.0;  // -135°
    readonly double _endAngle   = 405 * Math.PI / 180.0;  // +225°

    readonly int _minValue = 0;
    readonly int _maxValue = 160;
    readonly int _step = 20;
    
    readonly int _warningValue = 100;
    readonly int _dangerValue = 140;
    
    public Speedometer()
    {
        DataSourceChanged += (s, e) =>
        {
            if (SpeedometerDataSource is null)
                return;
            SpeedometerDataSource.OnDataReceived += (sender, args) => { Dispatcher.UIThread.Invoke(() =>
            {
                _currentValue = args.Value;
                InvalidateVisual();
            }); 
            };
            SpeedometerDataSource.StartListening();
        };
        InitializeComponent();
    }
    
    public override void Render(DrawingContext context)
    {
        base.Render(context);
        
        var center = new Point(Bounds.Width / 2, Bounds.Height / 2);
        double radius = Math.Min(Bounds.Width, Bounds.Height) / 2 - 5; // margin

        var whitePen = new Pen(Brushes.White, 6);
        var yellowPen = new Pen(Brushes.Yellow, 6);
        var redPen = new Pen(Brushes.Red, 6);

        var state = new InstrumentClusterSettingsState()
        {
            Center = center,
            Radius = radius,
            NormalPen = whitePen,
            WarningPen = yellowPen,
            DangerPen = redPen,
            MinimumValue = _minValue,
            MaximumValue = _maxValue,
            WarningValue = _warningValue,
            DangerValue = _dangerValue,
            StartAngle = _startAngle,
            EndAngle = _endAngle,
            StepValue = _step
        };
        
        // Vykreslení kruhu tachometru (tam, kde jsou čísla)
        var arc = InstrumentClusterDrawingHelper.CreateArcSegment(state, 0, _warningValue);
        context.DrawGeometry(null, whitePen, arc);
        arc = InstrumentClusterDrawingHelper.CreateArcSegment(state, _warningValue, _dangerValue);
        context.DrawGeometry(null, yellowPen, arc);
        arc = InstrumentClusterDrawingHelper.CreateArcSegment(state, _dangerValue, _maxValue);
        context.DrawGeometry(null, redPen, arc);

        // Vykreslení čísel a čárek tachometru
        var ticksAndNums = InstrumentClusterDrawingHelper.CreateArcTicksAndNumbers(state);
        foreach (Tuple<InstrumentClusterTick, InstrumentClusterNumber> ticksAndNum in ticksAndNums)
        {
            ticksAndNum.Item1.DisplayTick(context);
            ticksAndNum.Item2.DisplayNumber(context);
        }

        // Vykreslení ručičky tachometru
        var needle = InstrumentClusterDrawingHelper.DrawNeedle(state, _currentValue);
        context.DrawGeometry(null, whitePen, needle.Item1);
        context.DrawGeometry(null, redPen, needle.Item2);
    }
}