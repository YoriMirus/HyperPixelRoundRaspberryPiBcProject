using System;
using System.Globalization;
using System.Threading.Tasks;

using Avalonia.Media;
using Avalonia;
using CommunityToolkit.Mvvm.ComponentModel;

namespace DataCommunicationClient.ViewModels;

using CommunicationLibrary.InterProcessCommunication;
using CommunicationLibrary.TCPIPCommunication;

public partial class MainWindowViewModel : ViewModelBase , IDisposable
{
    //public NamedPipeSensorServer IPCServer { get; set; }
    public TcpSensorServer<double> TCPIPServer { get; set; }
    
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
        /*IPCServer = new NamedPipeSensorServer("SensorPipe");
        IPCServer.Start();*/

        TCPIPServer = new TcpSensorServer<double>();
        TCPIPServer.StartListening();
    }

    public async Task SendDataAsync()
    {
        //await IPCServer.SendAsync(DataToSend.ToString(CultureInfo.InvariantCulture));
        TCPIPServer.CurrentValue = _dataToSend;
    }
    
    public void Dispose()
    {
        //IPCServer.Dispose();
        TCPIPServer.Dispose();
    }
}