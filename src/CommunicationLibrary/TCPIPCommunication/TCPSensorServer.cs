using System.Net.Sockets;
using System.Net;
using System.Text.Json;

namespace CommunicationLibrary.TCPIPCommunication;

/// <summary>
/// Server na bázi TCP/IP, pomocí kterého se můžou odesílat data ze senzoru
/// </summary>
/// <typeparam name="T"></typeparam>
public class TcpSensorServer<T>
{
    private readonly int _port;
    private TcpListener? _listener;
    private CancellationTokenSource? _cts;
    private Task? _acceptTask;
    
    public T CurrentValue { get; set; }
    
    public TcpSensorServer(int port = 35653)
    {
        _port = port;
    }

    public void StartListening()
    {
        if (_acceptTask != null && !_acceptTask.IsCompleted)
            throw new InvalidOperationException("Server already running.");

        _cts = new CancellationTokenSource();
        _listener = new TcpListener(IPAddress.Loopback, _port);
        _listener.Start();

        _acceptTask = Task.Run(() => AcceptClientsAsync(_cts.Token));
    }

    public void StopListening()
    {
        _cts?.Cancel();
        _listener?.Stop();
    }

    private async Task AcceptClientsAsync(CancellationToken token)
    {
        while (!token.IsCancellationRequested)
        {
            try
            {
                TcpClient client = await _listener!.AcceptTcpClientAsync(token);
                _ = Task.Run(() => HandleClientAsync(client, token), token);
            }
            catch (OperationCanceledException)
            {
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine($"[TcpSensorServer] Accept error: {ex.Message}");
            }
        }
    }

    private async Task HandleClientAsync(TcpClient client, CancellationToken token)
    {
        Console.WriteLine($"Client connected: {client.Client.RemoteEndPoint}");
        using var stream = client.GetStream();
        using var writer = new StreamWriter(stream) { AutoFlush = true };

        try
        {
            while (!token.IsCancellationRequested && client.Connected)
            {
                var eventArgs = new SensorDataEventArgs<T>(DateTime.Now, CurrentValue);

                string json = JsonSerializer.Serialize(eventArgs);
                await writer.WriteLineAsync(json);

                await Task.Delay(50, token); // Send every 50ms
            }
        }
        catch (Exception ex)
        {
            Console.Error.WriteLine($"[TcpSensorServer] Client handling error: {ex.Message}");
        }
        finally
        {
            Console.WriteLine($"Client disconnected: {client.Client.RemoteEndPoint}");
        }
    }

    public void Dispose()
    {
        StopListening();
        _cts?.Dispose();
    }
}