using System.Device.I2c;
using CommunicationLibrary.I2CSensors.DTOs;

namespace CommunicationLibrary.I2CSensors;

public class MMA8452QAccelerometer : SensorBase<AccelerometerDTO, IDisposable>
{
    public static readonly int SlaveAddressHigh = 0b0011101;
    public static readonly int SlaveAddressLow = 0b0011100;
    private int DeviceScale { get; }
    private byte DeviceScaleBits { get; }

    protected override void InitialiseSensorImplementation(I2cDevice device)
    {
        // Po inicializaci musíme nastavit režim senzoru na aktivní
        // Ve výchozím je ve standby, při kterém sice funguje I2C komunikace, ale analogová část není funkční (a.k.a. nečte zrychlení)
        // Režim se nachází v registru 0x2A, jedná se o bit 0.
        // Můžou tam ale být další data (ve výchozím jsou 0, ale co když jsme restartovali program?), takže ho musíme celý přečíst, přepsat požadovaný bit a zapsat zpátky do registru
        Span<byte> registerValue = new Span<byte>([0]);
        device.WriteRead(new ReadOnlySpan<byte>([0x2A]), registerValue);

        // Nastavíme nultý bit na 1, s tím že ostatní bity neupravujeme
        registerValue[0] &= 0b11111110;
        registerValue[0] |= 0b1;
        
        // První byte zápisu nastavuje registr, do kterého píšeme, druhý byte nastavuje hodnotu
        device.Write(new ReadOnlySpan<byte>([0x2A, registerValue[0]]));
        
        
        // Udělejme to samé pro škálu
        registerValue = new Span<byte>([0]);
        device.WriteRead(new ReadOnlySpan<byte>([0x0E]), registerValue);

        registerValue[0] &= 0b11111100;
        registerValue[0] |= DeviceScaleBits;
        
        device.Write(new ReadOnlySpan<byte>([0x0E, registerValue[0]]));
    }

    protected override void OnSensorDisposing()
    {
        if (I2CDevice is null)
            return;
        
        // Nastavme senzor do standby, aby nebral energii zbytečně když na něj není nic připojeno
        Span<byte> registerValue = new Span<byte>([0]);
        I2CDevice.WriteRead(new ReadOnlySpan<byte>([0x2A]), registerValue);
        
        // Všechny bity necháme tak, jak jsou, ale nultý bit nastavíme na 0
        registerValue[0] &= 0b11111110;
        
        // První byte zápisu nastavuje registr, do kterého píšeme, druhý byte nastavuje hodnotu
        I2CDevice.Write(new ReadOnlySpan<byte>([0x2A, registerValue[0]]));
    }

    protected override AccelerometerDTO ReadSensorData()
    {
        if (I2CDevice is null)
            return new AccelerometerDTO();
        
        // Adresa 0x01 je první datová adresa
        // Máme 3 hodnoty na přečtení, celkem 12 bitů pro každý
        // Každá hodnota má teda dva registry. První registr obsahuje most significant bit, druhý least significant bit
        // Naštěstí nemusíme pro každý registr psát adresu znova. Když přečteme jeden registr, senzor automaticky přepne na druhý, takže stačí prostě číst 6 bytů
        // Sekvence registrů: OUT_X_MSB, OUT_X_LSB, OUT_Y_MSB, OUT_Y_LSB, OUT_Z_MSB, OUT_Z_LSB
        ReadOnlySpan<byte> registerAddress = new ReadOnlySpan<byte>([0x01]);
        Span<byte> data = new Span<byte>(new byte[6]);
        I2CDevice.WriteRead(registerAddress, data);
            
        byte OUT_X_MSB = data[0];
        byte OUT_X_LSB = data[1];
        byte OUT_Y_MSB = data[2];
        byte OUT_Y_LSB = data[3];
        byte OUT_Z_MSB = data[4];
        byte OUT_Z_LSB = data[5];

        short x = ConvertMSBLSBPairsToRawShort(OUT_X_MSB, OUT_X_LSB);
        short y = ConvertMSBLSBPairsToRawShort(OUT_Y_MSB, OUT_Y_LSB);
        short z = ConvertMSBLSBPairsToRawShort(OUT_Z_MSB, OUT_Z_LSB);

        // Akcelerometr má různé měřící škály. 
        // Pomocí nich se převádí short na double reprezentující výslednou akceleraci
        double countsPerG = 1024.0 * 2 / (DeviceScale);

        double xResult = x / countsPerG;
        double yResult = y / countsPerG;
        double zResult = z / countsPerG;

        return new AccelerometerDTO(xResult, yResult, zResult);
    }

    public MMA8452QAccelerometer(int i2CBusNumber, TimeSpan durationBetweenReads, int scale = 2) : base(i2CBusNumber, SlaveAddressLow, durationBetweenReads)
    {
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

    private short ConvertMSBLSBPairsToRawShort(byte MSB, byte LSB)
    {
        // Rád bych zde použil short, ale to se kompilátoru z nějakého důvodu nelíbí
        // MSB popisuje prvních 8 bitů čísla, LSB poslední 4. Tyto bity jsou ale nalevo, takže je musíme posunout doprava
        int result = (MSB << 4) | (LSB >> 4);

        // Poslední bit v MSB určuje znaménko
        // To znaménko, pokud je přítomno, musíme smazat z result a zapsat poslední čtyři bity na 1
        if ((MSB & (1 << 7)) != 0)
        {
            result |= (0b1111 << 12);
        }
        
        return (short)result;
    }
}