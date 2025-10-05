using System;
using System.IO;
using System.IO.Pipes;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;

namespace CommunicationLibrary.InterProcessCommunication;

/// <summary>
/// Klient, který poslouchá data ze senzoru přes Named Pipe a vyvolává události při příjmu nových dat.
/// </summary>
public class NamedPipeSensorClient : ISensorDataSource<string>
{
    private readonly string _pipeName;
    private CancellationTokenSource? _cts;
    private Task? _listeningTask;
    private NamedPipeClientStream? _pipeClient;

    public event SensorDataReceivedHandler<string>? OnDataReceived;

    public NamedPipeSensorClient(string pipeName)
    {
        _pipeName = pipeName;
    }

    /// <summary>
    /// Spustí naslouchání dat z Named Pipe.
    /// </summary>
    public void StartListening()
    {
        if (_listeningTask != null && !_listeningTask.IsCompleted)
            throw new InvalidOperationException("Client is already listening.");

        _cts = new CancellationTokenSource();
        _listeningTask = Task.Run(() => ListenAsync(_cts.Token));
    }

    /// <summary>
    /// Zastaví naslouchání.
    /// </summary>
    public void StopListening()
    {
        _cts?.Cancel();
        _pipeClient?.Dispose();
    }

    /// <summary>
    /// Hlavní poslouchací smyčka – připojí se k serveru a čte příchozí data.
    /// </summary>
    private async Task ListenAsync(CancellationToken token)
    {
        try
        {
            _pipeClient = new NamedPipeClientStream(".", _pipeName, PipeDirection.In);
            await _pipeClient.ConnectAsync(token);

            using var reader = new StreamReader(_pipeClient);

            while (!token.IsCancellationRequested && !_pipeClient.IsConnected)
                await Task.Delay(50, token);

            while (!token.IsCancellationRequested && _pipeClient.IsConnected)
            {
                string? json = await reader.ReadLineAsync();

                if (!string.IsNullOrWhiteSpace(json))
                {
                    try
                    {
                        // Expecting server to send JSON like: {"Timestamp":"2025-10-04T12:34:56.789Z","Value":42.7}
                        var data = JsonSerializer.Deserialize<SensorDataEventArgs<string>>(json);
                        if (data != null)
                        {
                            OnDataReceived?.Invoke(this, data);
                        }
                    }
                    catch (JsonException)
                    {
                    }
                }
            }
        }
        catch (OperationCanceledException)
        {
            /* Graceful stop */
        }
        catch (Exception ex)
        {
            Console.Error.WriteLine($"[NamedPipeSensorClient] Error: {ex.Message}");
        }
    }

    public void Dispose()
    {
        StopListening();
        _cts?.Dispose();
        _pipeClient?.Dispose();
    }
}
