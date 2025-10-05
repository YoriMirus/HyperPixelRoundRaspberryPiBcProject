using Avalonia;
using Avalonia.Controls;
using Avalonia.Input;
using Avalonia.Interactivity;
using Avalonia.Markup.Xaml;

namespace RoundDisplayAppGUI.Views;

public partial class SpeedometerSettings : UserControl
{
    public SpeedometerSettings()
    {
        InitializeComponent();
    }

    private void LoadIPFromFileButtonClicked(object? sender, RoutedEventArgs e)
    {
        
        
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
        // Stejný účel jako AbsornOnPointerPressed
        e.Handled = true;
    }
}