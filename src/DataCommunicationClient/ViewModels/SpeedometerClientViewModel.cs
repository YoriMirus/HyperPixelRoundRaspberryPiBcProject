namespace DataCommunicationClient.ViewModels;

using CommunicationLibrary;
using CommunicationLibrary.InterProcessCommunication;
using CommunicationLibrary.TCPIPCommunication;

public class SpeedometerClientViewModel : ViewModelBase
{
    public double MinValue
    {
        get => _minValue;
        set
        {
            _minValue = value;
            OnPropertyChanged();
        }
    }
    private double _minValue;

    public double MaxValue
    {
        get => _maxValue;
        set
        {
            _maxValue = value;
            OnPropertyChanged();
        }
    }
    private double _maxValue;

    public double Value
    {
        get => _value;
        set
        {
            _value = value;
            OnPropertyChanged();
        }
    }
    private double _value;

    public string PipeName
    {
        get => _pipeName;
        set
        {
            _pipeName = value;
            OnPropertyChanged();
        }
    }
    private string _pipeName;

    public int PortNum
    {
        get => _portNum;
        set
        {
            _portNum = value;
            OnPropertyChanged();
        }
    }
    private int _portNum;
    
    public ISensorDataServer<double>? Server { get; set; }
    
    public SpeedometerClientViewModel()
    {
        MinValue = 0;
        MaxValue = 160;
        Value = 80;

        _portNum = 35653;
        _pipeName = "Speedo";

        PropertyChanged += (s, e) =>
        {
            if (e.PropertyName == "Value" && Server is not null)
                Server.UpdateValue(Value);
        };
    }

    public void SetUpIPCServer()
    {
        if (Server is not null)
            Server.Stop();
        
        Server = new NamedPipeSensorServer<double>(Value, PipeName);
        Server.Start();
    }

    public void SetUpTCPIPServer()
    {
        if (Server is not null)
            Server.Stop();

        Server = new TcpSensorServer<double>(Value, PortNum);
        Server.Start();
    }
}