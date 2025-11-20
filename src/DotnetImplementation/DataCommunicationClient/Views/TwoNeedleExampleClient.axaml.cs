using Avalonia;
using Avalonia.Controls;
using Avalonia.Interactivity;
using Avalonia.Markup.Xaml;
using DataCommunicationClient.ViewModels;

namespace DataCommunicationClient.Views;

public partial class TwoNeedleExampleClient : UserControl
{
    public TwoNeedleExampleClient()
    {
        InitializeComponent();
    }
    
    private void TCPIPButtonClick(object? sender, RoutedEventArgs e)
    {
        if (DataContext is not TwoNeedleExampleClientViewModel vm)
            return;
        
        vm.SetUpTCPIPServer();
    }

    private void IPCButtonClick(object? sender, RoutedEventArgs e)
    {
        if (DataContext is not TwoNeedleExampleClientViewModel vm)
            return;
        
        vm.SetUpIPCServer();
    }
}