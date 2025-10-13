using Avalonia;
using Avalonia.Media;
using Avalonia.Controls;
using Avalonia.Markup.Xaml;
using Avalonia.Media;

using System;
using Avalonia.Threading;
using CommunicationLibrary.InterProcessCommunication;
using RoundDisplayAppGUI.Helpers;

namespace RoundDisplayAppGUI.Views;

public partial class TwoNeedleExample : UserControl
{
    public NamedPipeSensorClient<Tuple<double, double>> source;
    private Tuple<double, double> _currentValue;
    
    public TwoNeedleExample()
    {
        InitializeComponent();
        _currentValue = new Tuple<double, double>(0.0, 0.0);
        source = new NamedPipeSensorClient<Tuple<double, double>>("TwoValues");
        source.StartListening();
        source.OnDataReceived += (sender, args) => Dispatcher.UIThread.InvokeAsync(() =>
        {
            _currentValue = args.Value;
            InvalidateVisual();
        });
    }
    
    public override void Render(DrawingContext context)
    {
        base.Render(context);
        
        
        var center = new Point(Bounds.Width / 2, Bounds.Height / 2);
        double radius = Math.Min(Bounds.Width, Bounds.Height) / 2 - 5; // margin

        var whitePen = new Pen(Brushes.White, 6);
        var yellowPen = new Pen(Brushes.Yellow, 6);
        var redPen = new Pen(Brushes.Red, 6);
        
        // Nastavení pro levý senzor
        var leftInstrumentState = new InstrumentClusterSettingsState()
        {
            Center = center,
            Radius = radius,
            NormalPen = whitePen,
            WarningPen = yellowPen,
            DangerPen = redPen,
            MinimumValue = 0,
            MaximumValue = 100,
            WarningValue = 80,
            DangerValue = 80,
            StartAngle = 135 * Math.PI / 180.0, //-135°
            EndAngle = 225 * Math.PI / 180.0,  // -135° + 90°
            StepValue = 50,
            ReverseDirection = false
        };
        
        
        // Vykreslení kruhu tachometru (tam, kde jsou čísla)
        var arc = InstrumentClusterDrawingHelper.CreateArcSegment(leftInstrumentState, 0, leftInstrumentState.DangerValue);
        context.DrawGeometry(null, whitePen, arc);
        arc = InstrumentClusterDrawingHelper.CreateArcSegment(leftInstrumentState, leftInstrumentState.DangerValue, leftInstrumentState.MaximumValue);
        context.DrawGeometry(null, redPen, arc);
        
        // Vykreslení čísel a čárek tachometru
        var ticksAndNums = InstrumentClusterDrawingHelper.CreateArcTicksAndNumbers(leftInstrumentState);
        foreach (Tuple<InstrumentClusterTick, InstrumentClusterNumber> ticksAndNum in ticksAndNums)
        {
            ticksAndNum.Item1.DisplayTick(context);
            ticksAndNum.Item2.DisplayNumber(context);
        }

        // Levou ručičku posuňme trošku doleva. To vyžaduje nový stav, třída prozatím očekává stejný prostředek
        // Pro číslicovou řadu a pro ručičku přístroje
        // Musíme taky matematicky upravit minimální a maximální úhel, protože ručička bude ukazovat špatně
        var leftInstrumentNeedleState = InstrumentClusterDrawingHelper.ShiftNeedleByX(leftInstrumentState, -40);
        var leftNeedle = InstrumentClusterDrawingHelper.DrawNeedle(leftInstrumentNeedleState, _currentValue.Item1);
        
        context.DrawGeometry(null, whitePen, leftNeedle.Item1);
        context.DrawGeometry(null, redPen, leftNeedle.Item2);
        
        // Nastavení pro pravý senzor
        var rightInstrumentState = leftInstrumentState.Clone();
        rightInstrumentState.ReverseDirection = false;
        rightInstrumentState.StartAngle = (135 - 90) * Math.PI / 180.0; 
        rightInstrumentState.EndAngle = (135 - 180) * Math.PI / 180.0;
        
        // Vykreslení kruhu tachometru (tam, kde jsou čísla)
        arc = InstrumentClusterDrawingHelper.CreateArcSegment(rightInstrumentState, 0, rightInstrumentState.DangerValue);
        context.DrawGeometry(null, whitePen, arc);
        arc = InstrumentClusterDrawingHelper.CreateArcSegment(rightInstrumentState, rightInstrumentState.DangerValue, rightInstrumentState.MaximumValue);
        context.DrawGeometry(null, redPen, arc);
        
        // Vykreslení čísel a čárek tachometru
        ticksAndNums = InstrumentClusterDrawingHelper.CreateArcTicksAndNumbers(rightInstrumentState);
        foreach (Tuple<InstrumentClusterTick, InstrumentClusterNumber> ticksAndNum in ticksAndNums)
        {
            ticksAndNum.Item1.DisplayTick(context);
            ticksAndNum.Item2.DisplayNumber(context);
        }
        
        // Pravá ručička, taky posunutá stejně jak ta levá
        var rightInstrumentNeedleState = InstrumentClusterDrawingHelper.ShiftNeedleByX(rightInstrumentState, 40);
        var rightNeedle = InstrumentClusterDrawingHelper.DrawNeedle(rightInstrumentNeedleState, _currentValue.Item2);
        
        context.DrawGeometry(null, whitePen, rightNeedle.Item1);
        context.DrawGeometry(null, redPen, rightNeedle.Item2);
    }
}