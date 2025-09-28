using Avalonia;
using Avalonia.Controls.ApplicationLifetimes;
using Avalonia.Data.Core;
using Avalonia.Data.Core.Plugins;
using System.Linq;
using Avalonia.Markup.Xaml;
using RoundDisplayAppGUI.ViewModels;
using RoundDisplayAppGUI.Views;

namespace RoundDisplayAppGUI;

/* Inicializační kód pro Avalonia framework
 * Součástí Avalonia.MVVM template
 * Hledá View a ViewModel, které se nachází v projektu pomocí reflection a aplikuje je, pokud jsou potřeba.
 * Více o MVVM struktuře: https://learn.microsoft.com/cs-cz/dotnet/architecture/maui/mvvm
 *
 * Doporučuju na tento kód nesahat.
 *
 * Hlavní kód se nachází v Views/MainWindow a ViewModels/MainWindowViewModel
 */


public partial class App : Application
{
    public override void Initialize()
    {
        AvaloniaXamlLoader.Load(this);
    }

    public override void OnFrameworkInitializationCompleted()
    {
        if (ApplicationLifetime is IClassicDesktopStyleApplicationLifetime desktop)
        {
            // Avoid duplicate validations from both Avalonia and the CommunityToolkit. 
            // More info: https://docs.avaloniaui.net/docs/guides/development-guides/data-validation#manage-validationplugins
            DisableAvaloniaDataAnnotationValidation();
            desktop.MainWindow = new MainWindow
            {
                DataContext = new MainWindowViewModel(),
            };
        }

        base.OnFrameworkInitializationCompleted();
    }

    private void DisableAvaloniaDataAnnotationValidation()
    {
        // Get an array of plugins to remove
        var dataValidationPluginsToRemove =
            BindingPlugins.DataValidators.OfType<DataAnnotationsValidationPlugin>().ToArray();

        // remove each entry found
        foreach (var plugin in dataValidationPluginsToRemove)
        {
            BindingPlugins.DataValidators.Remove(plugin);
        }
    }
}