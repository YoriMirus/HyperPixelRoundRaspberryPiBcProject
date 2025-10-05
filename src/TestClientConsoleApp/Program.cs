
using CommunicationLibrary;
using CommunicationLibrary.InterProcessCommunication;

namespace TestConsoleApp;

static class Program
{
    static void Main()
    {
        var client = new NamedPipeSensorClient("SensorPipe");

        client.OnDataReceived += (sender, e) =>
        {
            Console.WriteLine($"[{e.Timestamp:HH:mm:ss.fff}] Received value: {e.Value}");
        };

        client.StartListening();

        Console.WriteLine("Listening for sensor data... Press any key to exit.");
        Console.ReadKey();

        client.StopListening();
    }
}