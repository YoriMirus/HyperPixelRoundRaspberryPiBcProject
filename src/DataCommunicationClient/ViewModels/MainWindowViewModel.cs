using System;
using System.Globalization;
using System.Threading.Tasks;

using Avalonia.Media;
using Avalonia;
using CommunicationLibrary;
using CommunityToolkit.Mvvm.ComponentModel;

namespace DataCommunicationClient.ViewModels;

using CommunicationLibrary.InterProcessCommunication;
using CommunicationLibrary.TCPIPCommunication;

public partial class MainWindowViewModel : ViewModelBase
{
    public SpeedometerClientViewModel SpeedoVM { get; set; }
    
    
    public MainWindowViewModel()
    {
        SpeedoVM = new SpeedometerClientViewModel();
    }
}