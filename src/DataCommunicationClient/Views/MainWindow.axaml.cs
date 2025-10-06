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

    private void Slider_OnValueChanged(object? sender, RangeBaseValueChangedEventArgs e)
    {
        if (DataContext is null)
            return;

        ((MainWindowViewModel)DataContext).SendData();
    }
}