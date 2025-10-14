using System;
using System.IO;
using System.Reflection;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Input;
using Avalonia.Interactivity;
using Avalonia.Markup.Xaml;

using CommunicationLibrary.InterProcessCommunication;
using CommunicationLibrary.TCPIPCommunication;

using RoundDisplayAppGUI.ViewModels;

namespace RoundDisplayAppGUI.Views;

public partial class SpeedometerSettings : UserControl
{
    public SpeedometerSettings()
    {
        InitializeComponent();
    }

    private void LoadIPFromFileButtonClicked(object? sender, RoutedEventArgs e)
    {
        string filePath = Assembly.GetExecutingAssembly().Location;
        string[] fileSplit = filePath.Split('/', '\\');
        fileSplit[^1] = "SpeedoIP.txt";
        filePath = string.Join('/', fileSplit);

        if (!File.Exists(filePath))
            return;
        
        IPAddressTextBox.Text = File.ReadAllText(filePath).Trim();
    }

    private void OnSelectionChanged(object? sender, SelectionChangedEventArgs e)
    {
        if (SelectionComboBox is null)
            return;
        
        if (SelectionComboBox.SelectedIndex == 0)
        {
            TcpIpGrid.IsVisible = true;
            ProcessGrid.IsVisible = false;
        }
        else
        {
            TcpIpGrid.IsVisible = false;
            ProcessGrid.IsVisible = true;
        }
    }

    private void LoadPipeNameFromFileButtonClicked(object? sender, RoutedEventArgs e)
    {
        string filePath = Assembly.GetExecutingAssembly().Location;
        string[] fileSplit = filePath.Split('/', '\\');
        fileSplit[^1] = "SpeedoPipeName.txt";
        filePath = string.Join('/', fileSplit);

        if (!File.Exists(filePath))
            return;
        
        PipeNameTextBox.Text = File.ReadAllText(filePath).Trim();
    }
    private void AbsorbOnPointerPressed(object? sender, PointerPressedEventArgs e)
    {
        // Absorbuj kliknutí myši, aby se nezapla swipe animace v samotném okně.
        // Když klikneš na Control v Avalonii, pokud se nenastaví e.Handled na true, event se přepošle na rodiče, který pokud to taky nesetne, tak se to dostane výš a výš
        // Tímtopádem se spustí OnPointerPressed na okně, což my rozhodně nechceme
        // Tato metoda je dána na každý control, jehož zmáčknutí nesmí spustit swipe
        e.Handled = true;
    }

    private void AbsorbOnPointerReleased(object? sender, PointerReleasedEventArgs e)
    {
        // Stejný účel jako AbsorbOnPointerPressed
        e.Handled = true;
    }

    private void ApplySettingsButtonClicked(object? sender, RoutedEventArgs e)
    {
        // TCP/IP
        if (SelectionComboBox.SelectedIndex == 0)
        {
            if (IPAddressTextBox.Text is null)
                return;
            string ipAddress = IPAddressTextBox.Text;
            Speedometer.SpeedometerDataSource = new TcpSensorClient<double>(ipAddress);
        }
        // PipeName IPC
        else if (SelectionComboBox.SelectedIndex == 1)
        {
            if (PipeNameTextBox.Text is null)
                return;
            var pipeName = PipeNameTextBox.Text;
            Speedometer.SpeedometerDataSource = new NamedPipeSensorClient<double>(pipeName);
        }
    }
}