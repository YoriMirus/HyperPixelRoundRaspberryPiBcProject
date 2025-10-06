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

public partial class MainWindowViewModel : ViewModelBase , IDisposable
{
    public ISensorDataServer<double> Server { get; set; }
    
    public double DataToSend
    {
        get => _dataToSend;
        set
        {
            _dataToSend = value;
            OnPropertyChanged();
        } 
    }

    private double _dataToSend;
    
    public MainWindowViewModel()
    {
        Server = new NamedPipeSensorServer<double>(0.0, "Speedo");
        Server.Start();
    }

    public void SendData()
    {
        Server.UpdateValue(_dataToSend);
    }
    
    public void Dispose()
    {
        Server.Dispose();
    }
}