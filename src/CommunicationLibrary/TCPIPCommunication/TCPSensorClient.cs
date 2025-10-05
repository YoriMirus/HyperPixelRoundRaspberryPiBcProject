using System;
using System.Text.Json;
using System.Net.Sockets;

namespace CommunicationLibrary.TCPIPCommunication;


public class TcpSensorClient<T> : ISensorDataSource<T>
{
    private readonly string _host;
    private readonly int _port;
    private TcpClient? _client;
    private CancellationTokenSource? _cts;
    private Task? _listenTask;

    public event SensorDataReceivedHandler<T>? OnDataReceived;

    public TcpSensorClient(string host, int port)
    {
        _host = host;
        _port = port;
    }

    public void StartListening()
    {
        if (_listenTask != null && !_listenTask.IsCompleted)
            throw new InvalidOperationException("Client already listening.");

        _cts = new CancellationTokenSource();
        _listenTask = Task.Run(() => ListenAsync(_cts.Token));
    }

    public void StopListening()
    {
        _cts?.Cancel();
        _client?.Close();
    }

    private async Task ListenAsync(CancellationToken token)
    {
        try
        {
            _client = new TcpClient();
            await _client.ConnectAsync(_host, _port);

            using var reader = new StreamReader(_client.GetStream());

            while (!token.IsCancellationRequested && _client.Connected)
            {  
                string? line = await reader.ReadLineAsync(token);
                if (!string.IsNullOrWhiteSpace(line))
                {
                    try
                    {
                        var eventArgs = JsonSerializer.Deserialize<SensorDataEventArgs<T>>(line);
                        if (eventArgs != null)
                            OnDataReceived?.Invoke(this, eventArgs);
                    }
                    catch (JsonException)
                    {
                    }
                }
            }
        }
        catch (OperationCanceledException)
        {
        }
        catch (Exception ex)
        {
            Console.Error.WriteLine($"[TcpSensorClient] Error: {ex.Message}");
        }
    }

    public void Dispose()
    {
        StopListening();
        _cts?.Dispose();
        _client?.Close();
    }
}