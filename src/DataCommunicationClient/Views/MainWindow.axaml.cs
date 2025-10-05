using Avalonia.Controls;
using Avalonia.Controls.Primitives;
using Avalonia.Interactivity;
using DataCommunicationClient.ViewModels;

namespace DataCommunicationClient.Views;

public partial class MainWindow : Window
{
    public MainWindow()
    {
        InitializeComponent();
    }

    private async void Button_OnClick(object? sender, RoutedEventArgs e)
    {
        if (DataContext is null)
            return;

        await ((MainWindowViewModel)DataContext).SendDataAsync();
    }

    private async void Slider_OnValueChanged(object? sender, RangeBaseValueChangedEventArgs e)
    {
        if (DataContext is null)
            return;

        await ((MainWindowViewModel)DataContext).SendDataAsync();
    }
}