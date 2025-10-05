namespace CommunicationLibrary.InterProcessCommunication;

using System;
using System.IO;
using System.IO.Pipes;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;


/// <summary>
/// Serverová část komunikace přes Named Pipe — odesílá data senzoru klientovi.
/// </summary>
public class NamedPipeSensorServer<T> : IDisposable
{
    private readonly string _pipeName;
    private NamedPipeServerStream? _pipeServer;
    private StreamWriter? _writer;
    private CancellationTokenSource? _cts;
    private Task? _serverTask;

    /// <summary>
    /// Inicializuje server s daným názvem roury.
    /// </summary>
    public NamedPipeSensorServer(string pipeName)
    {
        _pipeName = pipeName;
    }

    /// <summary>
    /// Spustí server a čeká na připojení klienta.
    /// </summary>
    public void Start()
    {
        if (_serverTask != null && !_serverTask.IsCompleted)
            throw new InvalidOperationException("Server is already running.");

        _cts = new CancellationTokenSource();
        _serverTask = Task.Run(() => RunServerAsync(_cts.Token));
    }

    /// <summary>
    /// Ukončí server.
    /// </summary>
    public void Stop()
    {
        _cts?.Cancel();
        _writer?.Dispose();
        _pipeServer?.Dispose();
    }

    /// <summary>
    /// Odesílá data klientovi (pokud je připojen).
    /// </summary>
    public async Task SendAsync(T value)
    {
        if (_writer == null)
            return; // no client yet

        var data = new SensorDataEventArgs<T>(DateTime.Now, value);
        string json = JsonSerializer.Serialize(data);

        await _writer.WriteLineAsync(json);
        await _writer.FlushAsync();
    }

    private async Task RunServerAsync(CancellationToken token)
    {
        try
        {
            _pipeServer = new NamedPipeServerStream(_pipeName, PipeDirection.Out, 1, PipeTransmissionMode.Byte,
                PipeOptions.Asynchronous);
            Console.WriteLine($"[NamedPipeSensorServer] Waiting for client connection on '{_pipeName}'...");
            await _pipeServer.WaitForConnectionAsync(token);

            _writer = new StreamWriter(_pipeServer) { AutoFlush = true };
            Console.WriteLine("[NamedPipeSensorServer] Client connected.");

            while (!token.IsCancellationRequested)
            {
                await Task.Delay(100, token); // keep alive loop
            }
        }
        catch (OperationCanceledException)
        {
            // graceful stop
        }
        catch (Exception ex)
        {
            Console.Error.WriteLine($"[NamedPipeSensorServer] Error: {ex.Message}");
        }
    }

    public void Dispose()
    {
        Stop();
        _cts?.Dispose();
        _writer?.Dispose();
        _pipeServer?.Dispose();
    }
}

