using System.Device.I2c;
using CommunicationLibrary.I2CSensors.DTOs;

namespace CommunicationLibrary.I2CSensors;

public class MMA8452QAccelerometer : ISensorDataSource<AccelerometerDTO>
{
    public static readonly int SlaveAddressHigh = 0b0011101;
    public static readonly int SlaveAddressLow = 0b0011100;
    private int DurationBetweenReads { get; }
    private int DeviceScale { get; }
    private byte DeviceScaleBits { get; }
    private int I2CBusNumber { get; }
    
    private I2cDevice? Device { get; set; }
    
    public void Dispose()
    {
        StopListening();
    }

    public event SensorDataReceivedHandler<AccelerometerDTO>? OnDataReceived;
    public void StartListening()
    {
        if (Device is not null)
        {
            Device.Dispose();
            Device = null;
        }
        
        var i2CSettings = new I2cConnectionSettings(I2CBusNumber, SlaveAddressLow);
        Device = I2cDevice.Create(i2CSettings);
        
        // Po inicializaci musíme nastavit režim senzoru na aktivní
        // Ve výchozím je ve standby, při kterém sice funguje I2C komunikace, ale analogová část není funkční (a.k.a. nečte zrychlení)
        // Režim se nachází v registru 0x2A, jedná se o bit 0.
        // Můžou tam ale být další data (ve výchozím jsou 0, ale co když jsme restartovali program?), takže ho musíme celý přečíst, přepsat požadovaný bit a zapsat zpátky do registru
        Span<byte> registerValue = new Span<byte>([0]);
        Device.WriteRead(new ReadOnlySpan<byte>([0x2A]), registerValue);

        // Nastavíme nultý bit na 1, s tím že ostatní bity neupravujeme
        registerValue[0] &= 0b11111110;
        registerValue[0] |= 0b1;
        
        // První byte zápisu nastavuje registr, do kterého píšeme, druhý byte nastavuje hodnotu
        Device.Write(new ReadOnlySpan<byte>([0x2A, registerValue[0]]));
        
        
        // Udělejme to samé pro škálu
        registerValue = new Span<byte>([0]);
        Device.WriteRead(new ReadOnlySpan<byte>([0x0E]), registerValue);

        registerValue[0] &= 0b11111100;
        registerValue[0] |= DeviceScaleBits;
        
        Device.Write(new ReadOnlySpan<byte>([0x0E, registerValue[0]]));
        
        Task.Run(ReadingLoop);
    }

    public void StopListening()
    {
        if (Device is null)
            return;
        
        // Nastavme senzor do standby, aby nebral energii zbytečně když na něj není nic připojeno
        Span<byte> registerValue = new Span<byte>([0]);
        Device.WriteRead(new ReadOnlySpan<byte>([0x2A]), registerValue);
        
        // Všechny bity necháme tak, jak jsou, ale nultý bit nastavíme na 0
        registerValue[0] &= 0b11111110;
        
        // První byte zápisu nastavuje registr, do kterého píšeme, druhý byte nastavuje hodnotu
        Device.Write(new ReadOnlySpan<byte>([0x2A, registerValue[0]]));
        
        Device.Dispose();
        Device = null;
    }

    public MMA8452QAccelerometer(int i2CBusNumber, int durationBetweenReads, int scale = 2)
    {
        I2CBusNumber = i2CBusNumber;
        DurationBetweenReads = durationBetweenReads;
        DeviceScale = scale;

        switch (scale)
        {
            case 4:
                DeviceScaleBits = 0b01;
                break;
            case 8:
                DeviceScaleBits = 0b10;
                break;
            default:
                // Výchozí hodnota je 2. Pokud je zadána nepodporovaná škála, tak tam dejme 2.
                DeviceScale = 2;
                DeviceScaleBits = 0b00;
                break;
        }
    }
    
    private void ReadingLoop()
    {
        while (Device is not null)
        {
            // Adresa 0x01 je první datová adresa
            // Máme 3 hodnoty na přečtení, celkem 12 bitů pro každý
            // Každá hodnota má teda dva registry. První registr obsahuje most significant bit, druhý least significant bit
            // Naštěstí nemusíme pro každý registr psát adresu znova. Když přečteme jeden registr, senzor automaticky přepne na druhý, takže stačí prostě číst 6 bytů
            // Sekvence registrů: OUT_X_MSB, OUT_X_LSB, OUT_Y_MSB, OUT_Y_LSB, OUT_Z_MSB, OUT_Z_LSB
            ReadOnlySpan<byte> registerAddress = new ReadOnlySpan<byte>([0x01]);
            Span<byte> data = new Span<byte>(new byte[6]);
            Device.WriteRead(registerAddress, data);
            
            byte OUT_X_MSB = registerAddress[0];
            byte OUT_X_LSB = registerAddress[1];
            byte OUT_Y_MSB = registerAddress[2];
            byte OUT_Y_LSB = registerAddress[3];
            byte OUT_Z_MSB = registerAddress[4];
            byte OUT_Z_LSB = registerAddress[5];

            short x = ConvertMSBLSBPairsToRawShort(OUT_X_MSB, OUT_X_LSB);
            short y = ConvertMSBLSBPairsToRawShort(OUT_Y_MSB, OUT_Y_LSB);
            short z = ConvertMSBLSBPairsToRawShort(OUT_Z_MSB, OUT_Z_LSB);

            // Akcelerometr má různé měřící škály. 
            // Pomocí nich se převádí short na double reprezentující výslednou akceleraci
            double countsPerG = 1024.0 * 2 / (DeviceScale);

            double xResult = x / countsPerG;
            double yResult = y / countsPerG;
            double zResult = z / countsPerG;
            
            OnDataReceived?.Invoke(this, new SensorDataEventArgs<AccelerometerDTO>(DateTime.Now, new AccelerometerDTO(xResult, yResult, zResult)));
            
            Thread.Sleep(DurationBetweenReads);
        }
    }

    private short ConvertMSBLSBPairsToRawShort(byte MSB, byte LSB)
    {
        Console.WriteLine($"MSB:{Convert.ToString(MSB, 2)}");
        Console.WriteLine($"LSB:{Convert.ToString(LSB, 2)}");
        
        // Rád bych zde použil short, ale to se kompilátoru z nějakého důvodu nelíbí
        // MSB popisuje prvních 8 bitů čísla, LSB poslední 4. Tyto bity jsou ale nalevo, takže je musíme posunout doprava
        int result = (MSB << 4) | (LSB >> 4);

        // Poslední bit v MSB určuje znaménko
        // To znaménko, pokud je přítomno, musíme smazat z result a zapsat poslední čtyři bity na 1
        if ((MSB & (1 << 7)) != 0)
        {
            result = result | (0b1111 << 12);
        }

        Console.WriteLine($"Result: {Convert.ToString(result, 2)}");

        return (short)result;
    }
}