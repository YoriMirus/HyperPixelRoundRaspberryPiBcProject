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
            MinimumValue = 0,
            MaximumValue = 160,
            WarningValue = 100,
            DangerValue = 140,
            StartAngle = 135 * Math.PI / 180.0, //-135°
            EndAngle = 405 * Math.PI / 180.0,  // +225°
            StepValue = 20
        };
        
        // Vykreslení kruhu tachometru (tam, kde jsou čísla)
        var arc = InstrumentClusterDrawingHelper.CreateArcSegment(state, 0, state.WarningValue);
        context.DrawGeometry(null, whitePen, arc);
        arc = InstrumentClusterDrawingHelper.CreateArcSegment(state, state.WarningValue, state.DangerValue);
        context.DrawGeometry(null, yellowPen, arc);
        arc = InstrumentClusterDrawingHelper.CreateArcSegment(state, state.DangerValue, state.MaximumValue);
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