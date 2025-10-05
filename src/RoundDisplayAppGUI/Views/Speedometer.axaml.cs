using System;
using System.Globalization;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Markup.Xaml;
using Avalonia.Media;
using Avalonia.Threading;
using CommunicationLibrary;

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
    private static ISensorDataSource<double> _speedoDataSource;
    private static event EventHandler? DataSourceChanged;

    private double _currentValue = 0.0;
    
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
        
        // Vykreslení kruhu tachometru (tam, kde jsou čísla)
        var numberLineSegment = DrawArcSegment(center, radius, 0, _warningValue);
        context.DrawGeometry(null, whitePen, numberLineSegment);

        numberLineSegment = DrawArcSegment(center, radius, _warningValue, _dangerValue);
        context.DrawGeometry(null, yellowPen, numberLineSegment);

        numberLineSegment = DrawArcSegment(center, radius, _dangerValue, _maxValue);
        context.DrawGeometry(null, redPen, numberLineSegment);
        
        // Vykreslení čárek a čísel tachometru
        for (int value = _minValue; value <= _maxValue; value += _step)
        {
            Pen pen = whitePen;
            if (value >= _warningValue && value < _dangerValue)
                pen = yellowPen;
            else if (value >= _dangerValue)
                pen = redPen;
            
            double angle = ValueToAngle(value, _minValue, _maxValue);
            
            var tickStart = new Point(
                center.X + Math.Cos(angle) * (radius - 20),
                center.Y + Math.Sin(angle) * (radius - 20));
            var tickEnd = new Point(
                center.X + Math.Cos(angle) * radius,
                center.Y + Math.Sin(angle) * radius);

            context.DrawLine(pen, tickStart, tickEnd);

            var labelPos = new Point(
                center.X + Math.Cos(angle) * (radius - 60),
                center.Y + Math.Sin(angle) * (radius - 60));

            var formatted = new FormattedText(value.ToString(), CultureInfo.CurrentCulture,
                FlowDirection.LeftToRight, Typeface.Default, 46, pen.Brush);

            context.DrawText(formatted,
                new Point(labelPos.X - formatted.Width / 2, labelPos.Y - formatted.Height / 2));
        }
        
        DrawNeedle(context, new Point(Bounds.Width / 2, Bounds.Height/2), radius, _currentValue);
    }
    
    StreamGeometry DrawArcSegment(Point center, double radius,
        double startVal, double endVal)
    {
        var geo = new StreamGeometry();
        using (var ctx = geo.Open())
        {
            // steps = vyhlazenost segmentu. Čím menší číslo, tím méně čár (jednodušší na GPU), ale budou více vidět nepřesnosti
            int steps = 40;
            for (int i = 0; i <= steps; i++)
            {
                double t = (double)i / steps;
                double val = startVal + t * (endVal - startVal);
                double angle = ValueToAngle(val, _minValue, _maxValue);

                var pt = new Point(center.X + Math.Cos(angle) * radius, center.Y + Math.Sin(angle) * radius);

                if (i == 0)
                    ctx.BeginFigure(pt, false);
                else
                    ctx.LineTo(pt);
            }
            ctx.EndFigure(false);
        }

        return geo;
    }
    double ValueToAngle(double value, double min, double max)
    {
        // Poměr hodnoty k maximu
        double t = (value - min) / (max - min);
        
        // Převeď na úhel
        return _startAngle + t * (_endAngle - _startAngle);
    }
    
    private void DrawNeedle(DrawingContext context, Point pivot, double radius, double value)
    {
        // Úhel natočení ručičky
        double angle = ValueToAngle(value, _minValue, _maxValue);

        // Paramety ručičky
        double needleLength = radius * 0.9;
        double needleWidth = radius * 0.03;

        // Směrový vektor
        double dx = Math.Cos(angle);
        double dy = Math.Sin(angle);

        // Pravoúhlý vektor
        var perp = new Vector(-dy, dx);

        // Špička ručičky
        var tip = new Point(pivot.X + dx * needleLength,
            pivot.Y + dy * needleLength);

        // Základ ručičky (2 body, protože děláme trojúhelník)
        var baseLeft = new Point(pivot.X - dx * 15 + perp.X * needleWidth,
            pivot.Y - dy * 15 + perp.Y * needleWidth);
        var baseRight = new Point(pivot.X - dx * 15 - perp.X * needleWidth,
            pivot.Y - dy * 15 - perp.Y * needleWidth);

        // Postav trojúhelník
        var geo = new StreamGeometry();
        using (var ctx = geo.Open())
        {
            ctx.BeginFigure(baseLeft, true);
            ctx.LineTo(baseRight);
            ctx.LineTo(tip);
            ctx.EndFigure(true);
        }

        // Nakresli kruh uprostřed obrazovky
        double hubRadius = radius * 0.1;
        context.DrawEllipse(null, new Pen(Brushes.White, 3), pivot, hubRadius, hubRadius);
        
        // Nakresli ručičku
        context.DrawGeometry(Brushes.Red, null, geo);
    }
}