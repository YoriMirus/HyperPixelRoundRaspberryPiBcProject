// See https://aka.ms/new-console-template for more information

using CommunicationLibrary.I2CSensors;
using CommunicationLibrary;
using CommunicationLibrary.I2CSensors.DTOs;

Console.WriteLine("Tester senzorů. Zadej číslo i2c sběrnice (podívej se do /dev a zkus svůj senzor najít pomocí i2cdetect)");
string? input = "...";
int i2CBusNumber;
while (!int.TryParse(input, out i2CBusNumber))
{
    input = Console.ReadLine();
}

Console.WriteLine("Který senzor chceš použít?");
Console.WriteLine("0 = BMP180 GY-68 (nadmořská výška, atmosférický tlak, teplota)");
Console.WriteLine("1 = SHT30 (teplota, vlhkost)");
Console.WriteLine("2 = MMA8452Q akcelerometr");

IDisposable? sensor = null;

bool cancel = false;
while (!cancel)
{
    input = Console.ReadLine();
    switch (input)
    {
        case "0":
            var BmpSensor = new Bmp180Gy68PressureTemperatureSensor(i2CBusNumber, TimeSpan.FromMilliseconds(1000));
            BmpSensor.OnDataReceived += DataReceived;
            BmpSensor.StartListening();
            sensor = BmpSensor;
            cancel = true;
            break;
        case "1":
            var Sht30Sensor = new SHT3xHumidityTemperatureSensor(i2CBusNumber, TimeSpan.FromMilliseconds(1000));
            Sht30Sensor.OnDataReceived += Sht30SensorOnOnDataReceived;
            Sht30Sensor.StartListening();
            sensor = Sht30Sensor;
            cancel = true;
            break;
        case "2":
            var MMA8452Q = new MMA8452QAccelerometer(i2CBusNumber, TimeSpan.FromMilliseconds(100), 2);
            MMA8452Q.OnDataReceived += MMA8452QOnOnDataReceived;
            MMA8452Q.StartListening();
            sensor = MMA8452Q;
            cancel = true;
            break;
    }
}

while (!Console.KeyAvailable)
{
    
}

sensor?.Dispose();

return;

void DataReceived(object sender, SensorDataEventArgs<PressureTemperatureAltitudeDTO> e)
{
    Console.WriteLine("Nadmořská výška (m): " + e.Value.Altitude);
    Console.WriteLine("Atmosférický tlak (atm): " + e.Value.Pressure);
    Console.WriteLine("Teplota (°C): " + e.Value.Temperature);
}

void Sht30SensorOnOnDataReceived(object sender, SensorDataEventArgs<HumidityTemperatureDTO> e)
{
    Console.WriteLine("Teplota (°C): " + e.Value.Temperature);
    Console.WriteLine("Vlhkost (%): " + e.Value.Humidity);
}

void MMA8452QOnOnDataReceived(object sender, SensorDataEventArgs<AccelerometerDTO> e)
{
    Console.WriteLine($"X:Y:Z = {e.Value.AccelerationX}:{e.Value.AccelerationY}:{e.Value.AccelerationZ}");
}