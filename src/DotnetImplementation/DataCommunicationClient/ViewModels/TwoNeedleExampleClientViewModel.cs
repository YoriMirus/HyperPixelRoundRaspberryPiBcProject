namespace DataCommunicationClient.ViewModels;

using CommunicationLibrary;
using CommunicationLibrary.InterProcessCommunication;
using CommunicationLibrary.TCPIPCommunication;

using System;

public class TwoNeedleExampleClientViewModel : ViewModelBase
{
    public double MinValue1
    {
        get => _minValue1;
        set
        {
            _minValue1 = value;
            OnPropertyChanged();
        }
    }
    private double _minValue1;

    public double MaxValue1
    {
        get => _maxValue1;
        set
        {
            _maxValue1 = value;
            OnPropertyChanged();
        }
    }
    private double _maxValue1;

    public double Value1
    {
        get => _value1;
        set
        {
            _value1 = Math.Round(value, 1);;
            OnPropertyChanged();
        }
    }
    private double _value1;
    
    public double MinValue2
    {
        get => _minValue2;
        set
        {
            _minValue2 = value;;
            OnPropertyChanged();
        }
    }
    private double _minValue2;

    public double MaxValue2
    {
        get => _maxValue2;
        set
        {
            _maxValue2 = value;
            OnPropertyChanged();
        }
    }
    private double _maxValue2;

    public double Value2
    {
        get => _value2;
        set
        {
            _value2 = Math.Round(value, 1);;
            OnPropertyChanged();
        }
    }
    private double _value2;

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
    
    public ISensorDataServer<Tuple<double,double>>? Server { get; set; }
    
    public TwoNeedleExampleClientViewModel()
    {
        MinValue1 = 0;
        MaxValue1 = 100;
        MinValue2 = 0;
        MaxValue2 = 100;
        Value1= 80;
        Value2 = 80;

        _portNum = 35653;
        _pipeName = "TwoValues";

        PropertyChanged += (s, e) =>
        {
            if ((e.PropertyName == "Value1" || e.PropertyName == "Value2") && Server is not null)
                Server.UpdateValue(new Tuple<double, double>(Value1, Value2));
        };
    }

    public void SetUpIPCServer()
    {
        if (Server is not null)
            Server.Stop();
        
        Server = new NamedPipeSensorServer<Tuple<double,double>>(new Tuple<double, double>(Value1, Value2), PipeName);
        Server.Start();
    }

    public void SetUpTCPIPServer()
    {
        if (Server is not null)
            Server.Stop();

        Server = new TcpSensorServer<Tuple<double,double>>(new Tuple<double, double>(Value1, Value2), PortNum);
        Server.Start();
    }
}