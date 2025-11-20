
using CommunicationLibrary;
using CommunicationLibrary.InterProcessCommunication;
using CommunicationLibrary.TCPIPCommunication;

namespace TestConsoleApp;

static class Program
{
    static void Main()
    {
        /*
        var client = new NamedPipeSensorClient("SensorPipe");

        client.OnDataReceived += (sender, e) =>
        {
            Console.WriteLine($"[{e.Timestamp:HH:mm:ss.fff}] Received value: {e.Value}");
        };

        client.StartListening();

        Console.WriteLine("Listening for sensor data... Press any key to exit.");
        Console.ReadKey();

        client.StopListening();*/
        
        var client = new TcpSensorClient<string>("127.0.0.1", 35653); // replace with server IP

        client.OnDataReceived += (s, e) =>
        {
            Console.WriteLine($"[{e.Timestamp:HH:mm:ss.fff}] Received value: {e.Value:F2}");
        };

        client.StartListening();

        Console.WriteLine("TCP sensor client running. Press any key to stop.");
        Console.ReadKey();
        client.StopListening();
    }
}