using Avalonia;
using Avalonia.Controls;
using Avalonia.Markup.Xaml;

namespace RoundDisplayAppGUI.Views;

using Mapsui;
using Mapsui.Tiling;
using Mapsui.Projections;

public partial class MapWidget : UserControl
{
    public MapWidget()
    {
        this.PointerPressed += (sender, args) =>
        {
            args.Handled = true;
        };
        InitializeComponent();
        var mapControl = new Mapsui.UI.Avalonia.MapControl();
        
        mapControl.Map?.Layers.Add(Mapsui.Tiling.OpenStreetMap.CreateTileLayer());

        var center = SphericalMercator.FromLonLat(18.1603213,49.8315196);

        mapControl.Map?.Navigator.CenterOnAndZoomTo(new MPoint(center.x, center.y), 10);
        
        Content = mapControl;
    }
}