using Avalonia;
using Avalonia.Controls;
using Avalonia.Input;
using Avalonia.Layout;
using Avalonia.Markup.Xaml;

namespace RoundDisplayAppGUI.Views;

using Mapsui;
using Mapsui.Tiling;
using Mapsui.Projections;

public partial class MapWidget : UserControl
{
    public MapWidget()
    {
        InitializeComponent();
        
        Map.Map?.Layers.Add(OpenStreetMap.CreateTileLayer());

        var center = SphericalMercator.FromLonLat(18.1603213,49.8315196);

        Map.Map?.Navigator.CenterOnAndZoomTo(new MPoint(center.x, center.y), 10);
    }

    private void Map_OnPointerPressed(object? sender, PointerPressedEventArgs e)
    {
        e.Handled = true;
    }
}