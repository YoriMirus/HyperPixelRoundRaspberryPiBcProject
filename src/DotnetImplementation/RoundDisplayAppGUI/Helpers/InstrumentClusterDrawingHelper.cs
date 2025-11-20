namespace RoundDisplayAppGUI.Helpers;

using Avalonia;
using Avalonia.Media;

using System;
using System.Globalization;
using System.Collections.Generic;

/// <summary>
/// Objekt reprezentující design přístrojovky.
/// Obsahuje podstatné informace jako kde se kreslí číslová křivka, minimální hodnota, maximální hodnota, atd.
/// </summary>
public class InstrumentClusterSettingsState
{
    /// <summary>
    /// Poloměr kružnice, která reprezentuje vzdálenost od prostředku k číselné ose
    /// </summary>
    public double Radius { get; set; }
    /// <summary>
    /// Nejmenší povolená hodnota
    /// </summary>
    public int MinimumValue { get; set; }
    /// <summary>
    /// Největší povolená hodnota
    /// </summary>
    public int MaximumValue { get; set; }
    /// <summary>
    /// Kde směřuje ručička přístrojovky, když má směřovat na nejmenší hodnotu
    /// </summary>
    public double StartAngle { get; set; }
    /// <summary>
    /// Kde směřuje ručička přístrojovky, když má směřovat na největší hodnotu
    /// </summary>
    public double EndAngle { get; set; }
    /// <summary>
    /// Koordinace ke středu přístrojovky
    /// </summary>
    public Point Center { get; set; }
    /// <summary>
    /// Jaká hodnota značí varovnou zónu
    /// </summary>
    public int WarningValue { get; set; }
    /// <summary>
    /// Jaká hodnota značí nebezpečnou zónu
    /// </summary>
    public int DangerValue { get; set; }
    /// <summary>
    /// Číselná vzdálenost mezi čísly na číselná ose
    /// </summary>
    public int StepValue { get; set; }
    /// <summary>
    /// Použij tuto metodu, pokud ručička ukazuje přesně opačně od číselné osy (všude, jenom ne na ní)
    /// </summary>
    public bool ReverseDirection { get; set; }
    
    public required Pen NormalPen { get; set; }
    public required Pen WarningPen { get; set; }
    public required Pen DangerPen { get; set; }

    public InstrumentClusterSettingsState Clone()
    {
        return new InstrumentClusterSettingsState()
        {
            Center = Center,
            DangerPen = DangerPen,
            WarningPen = WarningPen,
            NormalPen = NormalPen,
            WarningValue = WarningValue,
            DangerValue = DangerValue,
            StepValue = StepValue,
            Radius = Radius,
            MinimumValue = MinimumValue,
            MaximumValue = MaximumValue,
            StartAngle = StartAngle,
            EndAngle = EndAngle,
        };
    }
}

public class InstrumentClusterTick
{
    public required Point TickStart { get; set; }
    public required Point TickEnd { get; set; }
    public required Pen Pen { get; set; }

    public void DisplayTick(DrawingContext context)
    {
        context.DrawLine(Pen, TickStart, TickEnd);
    }
}

public class InstrumentClusterNumber
{
    public required FormattedText Text { get; set; }
    public required Point TextLocation { get; set; }

    public void DisplayNumber(DrawingContext context)
    {
        context.DrawText(Text, new Point(TextLocation.X - Text.Width / 2, TextLocation.Y - Text.Height / 2));
    }
}

public static class InstrumentClusterDrawingHelper
{
    /// <summary>
    /// Nakreslí křivku podél fiktivní kružnice.
    /// Délka křivky záleží na hodnotách přístrojovky.
    /// </summary>
    /// <param name="state">Jak je nakonfigurovaná přistrojovka</param>
    /// <param name="startValue">Jaká je počáteční hodnota číselné osy, od které se má kreslit křivka</param>
    /// <param name="endValue">Kde má křivka skončit</param>
    /// <returns>Křivku, kterou lze vykreslit pomocí DrawingContext</returns>
    public static StreamGeometry CreateArcSegment(InstrumentClusterSettingsState state, double startValue, double endValue)
    {
        var geo = new StreamGeometry();
        using (var ctx = geo.Open())
        {
            // steps = vyhlazenost segmentu. Čím menší číslo, tím méně čár (jednodušší na GPU), ale budou více vidět nepřesnosti
            int steps = 40;
            for (int i = 0; i <= steps; i++)
            {
                double t = (double)i / steps;
                double val = startValue + t * (endValue - startValue);
                double angle = ValueToAngle(state, val);

                var pt = new Point(state.Center.X + Math.Cos(angle) * state.Radius, state.Center.Y + Math.Sin(angle) * state.Radius);

                if (i == 0)
                    ctx.BeginFigure(pt, false);
                else
                    ctx.LineTo(pt);
            }
            ctx.EndFigure(false);
        }

        return geo;
    }

    public static List<Tuple<InstrumentClusterTick, InstrumentClusterNumber>> CreateArcTicksAndNumbers(
        InstrumentClusterSettingsState state)
    {
        var result = new List<Tuple<InstrumentClusterTick, InstrumentClusterNumber>>();
        for (int value = state.MinimumValue; value <= state.MaximumValue; value += state.StepValue)
        {
            Pen pen = state.NormalPen;
            if (value >= state.WarningValue && value < state.DangerValue)
                pen = state.WarningPen;
            else if (value >= state.DangerValue)
                pen = state.DangerPen;
            
            double angle = ValueToAngle(state, value);
            
            var tickStart = new Point(
                state.Center.X + Math.Cos(angle) * (state.Radius - 20),
                state.Center.Y + Math.Sin(angle) * (state.Radius - 20));
            var tickEnd = new Point(
                state.Center.X + Math.Cos(angle) * state.Radius,
                state.Center.Y + Math.Sin(angle) * state.Radius);


            var labelPos = new Point(
                state.Center.X + Math.Cos(angle) * (state.Radius - 60),
                state.Center.Y + Math.Sin(angle) * (state.Radius - 60));

            var formatted = new FormattedText(value.ToString(), CultureInfo.CurrentCulture,
                FlowDirection.LeftToRight, Typeface.Default, 46, pen.Brush);

            var tick = new InstrumentClusterTick()
            {
                Pen = pen,
                TickStart = tickStart,
                TickEnd = tickEnd
            };

            var num = new InstrumentClusterNumber()
            {
                Text = formatted,
                TextLocation = labelPos
            };
            
            result.Add(new Tuple<InstrumentClusterTick, InstrumentClusterNumber>(tick, num));
        }

        return result;
    }
    
    public static Tuple<EllipseGeometry, StreamGeometry> DrawNeedle(InstrumentClusterSettingsState state, double value)
    {
        // Úhel natočení ručičky
        double angle = ValueToAngle(state, value);

        // Paramety ručičky
        double needleLength = state.Radius * 0.9;
        double needleWidth = state.Radius * 0.03;

        // Směrový vektor
        double dx = Math.Cos(angle);
        double dy = Math.Sin(angle);

        // Pravoúhlý vektor
        var perp = new Vector(-dy, dx);

        // Špička ručičky
        var tip = new Point(state.Center.X + dx * needleLength,
            state.Center.Y + dy * needleLength);

        // Základ ručičky (2 body, protože děláme trojúhelník)
        var baseLeft = new Point(state.Center.X - dx * 15 + perp.X * needleWidth,
            state.Center.Y - dy * 15 + perp.Y * needleWidth);
        var baseRight = new Point(state.Center.X - dx * 15 - perp.X * needleWidth,
            state.Center.Y - dy * 15 - perp.Y * needleWidth);

        // Postav trojúhelník (samotná ručka tachometru)
        var geo = new StreamGeometry();
        using (var ctx = geo.Open())
        {
            ctx.BeginFigure(baseLeft, true);
            ctx.LineTo(baseRight);
            ctx.LineTo(tip);
            ctx.EndFigure(true);
        }
        
        // Nakresli kruh uprostřed obrazovky
        double hubRadius = state.Radius * 0.1;
        var ellipse = new EllipseGeometry()
        {
            Center = state.Center,
            RadiusX = hubRadius,
            RadiusY = hubRadius
        };

        return new Tuple<EllipseGeometry, StreamGeometry>(ellipse, geo);
    }

    /// <summary>
    /// Vytvoří nové nastavení přístrojovky, ve kterém jsou upraveny hodnoty StartAngle a EndAngle, Radius a Center tak,
    /// aby kresba ručičky byla přesná, i když ručička se nenachází v prostředku kružnice, pomocí které byla nakreslena číslicová křivka
    /// </summary>
    /// <param name="state"></param>
    /// <param name="xValue">Hondnota x, po které byl tachometr posunut. Kladné hodnoty směřují doprava, záporné doleva</param>
    /// <returns></returns>
    public static InstrumentClusterSettingsState ShiftNeedleByX(InstrumentClusterSettingsState state, double xValue)
    {
        // Úprava úhlu
        var start = new Point(
            state.Center.X + Math.Cos(state.StartAngle) * state.Radius,
            state.Center.Y + Math.Sin(state.StartAngle) * state.Radius);

        var end = new Point(
            state.Center.X + Math.Cos(state.EndAngle) * state.Radius,
            state.Center.Y + Math.Sin(state.EndAngle) * state.Radius);

        // new pivot moved left by dx
        var newPivot = new Point(state.Center.X + xValue, state.Center.Y);

        // angles from new pivot to the same arc points
        double newMinAngle = Math.Atan2(start.Y - newPivot.Y, start.X - newPivot.X);
        double newMaxAngle = Math.Atan2(end.Y   - newPivot.Y, end.X   - newPivot.X);
        
        if (state.ReverseDirection)
            newMaxAngle += 2 * Math.PI;
        
        var instrumentNeedleState = state.Clone();
        
        instrumentNeedleState.StartAngle = newMinAngle;
        instrumentNeedleState.EndAngle = newMaxAngle;

        instrumentNeedleState.Center = new Point(state.Center.X + xValue, state.Center.Y);
        instrumentNeedleState.Radius -= 40;
        
        return instrumentNeedleState;
    }
    
    
    private static double ValueToAngle(InstrumentClusterSettingsState state, double value)
    {
        // Poměr hodnoty k maximu
        double t = (value - state.MinimumValue) / (state.MaximumValue - state.MinimumValue);
        
        // Převeď na úhel
        return state.StartAngle + t * (state.EndAngle - state.StartAngle);
    }
}