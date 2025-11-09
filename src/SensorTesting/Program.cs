// See https://aka.ms/new-console-template for more information

using CommunicationLibrary.I2CSensors;
using CommunicationLibrary;

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

ISensorDataSource<Tuple<double,double,double>>? BmpSensor = null;
ISensorDataSource<Tuple<double, double>>? Sht30Sensor = null;

bool cancel = false;
while (!cancel)
{
    input = Console.ReadLine();
    switch (input)
    {
        case "0":
            BmpSensor = new Bmp180Gy68PressureTemperatureSensor(i2CBusNumber, 1000);
            BmpSensor.OnDataReceived += DataReceived;
            BmpSensor.StartListening();
            cancel = true;
            break;
        case "1":
            Sht30Sensor = new SHT3xHumidityTemperatureSensor(i2CBusNumber, 1000);
            Sht30Sensor.OnDataReceived += Sht30SensorOnOnDataReceived;
            Sht30Sensor.StartListening();
            cancel = true;
            break;
    }
}

while (!Console.KeyAvailable)
{
    
}

if (BmpSensor is not null)
    BmpSensor.Dispose();

if (Sht30Sensor is not null)
    Sht30Sensor.Dispose();

return;

void DataReceived(object sender, SensorDataEventArgs<Tuple<double, double, double>> e)
{
    Console.WriteLine("Nadmořská výška (m): " + e.Value.Item1);
    Console.WriteLine("Atmosférický tlak (atm): " + e.Value.Item2);
    Console.WriteLine("Teplota (°C): " + e.Value.Item3);
}

void Sht30SensorOnOnDataReceived(object sender, SensorDataEventArgs<Tuple<double, double>> e)
{
    Console.WriteLine("Teplota (°C): " + e.Value.Item1);
    Console.WriteLine("Vlhkost (%): " + e.Value.Item2);
}