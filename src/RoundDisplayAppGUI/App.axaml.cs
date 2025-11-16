using Avalonia;
using Avalonia.Controls.ApplicationLifetimes;
using Avalonia.Data.Core;
using Avalonia.Data.Core.Plugins;
using System.Linq;
using Avalonia.Markup.Xaml;
using RoundDisplayAppGUI.ViewModels;
using RoundDisplayAppGUI.Views;

using System;

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
    public static bool IsRaspberryPi { get; private set; }
    public override void Initialize()
    {
        AvaloniaXamlLoader.Load(this);
    }

    public override void OnFrameworkInitializationCompleted()
    {
        if (ApplicationLifetime is IClassicDesktopStyleApplicationLifetime desktop)
        {
            string hostName = Environment.MachineName;
            string userName =  Environment.UserName;

            IsRaspberryPi = hostName.Contains("raspberry") || hostName.Contains("rpi") ||
                                 userName.Contains("raspberry") || userName.Contains("rpi");
            
            // Avoid duplicate validations from both Avalonia and the CommunityToolkit. 
            // More info: https://docs.avaloniaui.net/docs/guides/development-guides/data-validation#manage-validationplugins
            DisableAvaloniaDataAnnotationValidation();
            desktop.MainWindow = new MainWindow()
            {
                DataContext = new MainWindowViewModel(),
            };

            Console.WriteLine("Host name: " + hostName);
            Console.WriteLine("User name: " + userName);
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