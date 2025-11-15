# HyperPixelRoundRaspberryPiBcProject

## Kompilace

Pro samotné grafické rozhraní stačí spustit příkaz
```dotnet run --project RoundDisplayAppGUI```

**POZOR!** na RaspberryPi OS je nutné ještě pár dodatečných kroků.
Skiasharp má aktuálně bug, kde na ARM verzi knihovny chybí pár závislostí v samotném .dll souboru.
Ty je nutné do něj vložit manuálně.

Otevřete kompilovanou složku, a spusťte následující kód:
Nainstalujte závislosti:
```
sudo apt-get update
sudo apt-get install patchelf
```

libSkiaSharp.so se nachází v PROJECT_DIR/Bin/Debug/net8.0/runtimes/linux-arm/native

Poté přidejte závislosti do projektu:
```
patchelf --add-needed libuuid.so.1 libSkiaSharp.so
pachelf --add-needed libfreetype.so.6 libSkiaSharp.so
```

Potvrďte, že jsou závislosti přidány následujícím příkazem
```
ldd libSkiaSharp.so
```

Nejnovější funkční verze libSkiaSharp, která tento problém nemá je 1.116.0, ta je ale příliš stará pro balíček Avalonia.Mapsui, takže to není aktuálně možné (maximálně, že by se použila beta verze 5.0.0-beta.17, ta ještě závisí na 3.116.1)
