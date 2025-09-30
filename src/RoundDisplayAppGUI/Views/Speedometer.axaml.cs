using System;
using System.Globalization;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Markup.Xaml;
using Avalonia.Media;

namespace RoundDisplayAppGUI.Views;

public partial class Speedometer : UserControl
{
    public Speedometer()
    {
        InitializeComponent();
    }
    
    public override void Render(DrawingContext context)
    {
        base.Render(context);

        var center = new Point(Bounds.Width / 2, Bounds.Height / 2);
        double radius = Math.Min(Bounds.Width, Bounds.Height) / 2 - 20; // margin

        // Dial parameters
        int minValue = 0;
        int maxValue = 120;
        int step = 30;

        var pen = new Pen(Brushes.White, 2);

        // Draw outer circle
        //context.DrawEllipse(null, pen, center, radius, radius);

        // Draw arc from 0° (left) to 180° (right)
        var geo = new StreamGeometry();
        using (var ctx = geo.Open())
        {
            var startPoint = new Point(center.X - radius, center.Y); // left side
            var endPoint   = new Point(center.X + radius, center.Y); // right side

            ctx.BeginFigure(startPoint, false); // not filled
            ctx.ArcTo(endPoint,
                new Size(radius, radius),
                0,  // rotation
                false, // largeArc
                SweepDirection.Clockwise);
            ctx.EndFigure(false);
        }

        context.DrawGeometry(null, pen, geo);
        
        // Draw tick marks and numbers
        for (int value = minValue; value <= maxValue; value += step)
        {
            // Map value to angle (e.g. -120° to +120° arc)
            double angle = Math.PI * (value - minValue) / (maxValue - minValue) + Math.PI;
            //double angle = Math.PI * (4.0 / 3.0) * (value - minValue) / (maxValue - minValue) - Math.PI / 6;

            // Tick start & end
            var tickStart = new Point(
                center.X + Math.Cos(angle) * (radius - 10),
                center.Y + Math.Sin(angle) * (radius - 10));
            var tickEnd = new Point(
                center.X + Math.Cos(angle) * radius,
                center.Y + Math.Sin(angle) * radius);

            context.DrawLine(pen, tickStart, tickEnd);

            // Label position (a bit inside radius)
            var labelPos = new Point(
                center.X + Math.Cos(angle) * (radius - 30),
                center.Y + Math.Sin(angle) * (radius - 30));


            
            /*var formatted = new FormattedText(
                value.ToString(),
                Typeface.Default,
                14,
                TextAlignment.Center,
                TextWrapping.NoWrap,
                Size.Infinity);*/

            var formatted = new FormattedText(value.ToString(), CultureInfo.CurrentCulture, FlowDirection.LeftToRight,
                Typeface.Default, 14, Brushes.White);
            
            // Draw text centered at labelPos
            context.DrawText(
                formatted,
                new Point(labelPos.X - formatted.Width / 2, labelPos.Y - formatted.Height / 2));
            
        }
    }
}