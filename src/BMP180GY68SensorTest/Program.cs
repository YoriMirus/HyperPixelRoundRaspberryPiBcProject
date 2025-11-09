// See https://aka.ms/new-console-template for more information

using CommunicationLibrary.I2CSensors;
using CommunicationLibrary;

Console.WriteLine("Tester senzoru BMP180 GY-68. Zadej číslo i2c sběrnice (podívej se do /dev a zkus svůj senzor najít pomocí i2cdetect)");
string? input = "...";
int i2CBusNumber = 0;
while (!int.TryParse(input, out i2CBusNumber))
{
    input = Console.ReadLine();
}

var sensor = new Bmp180Gy68PressureTemperatureSensor(i2CBusNumber, 1000);
sensor.OnDataReceived += DataReceived;
sensor.StartListening();

while (!Console.KeyAvailable)
{
    
}

sensor.OnDataReceived -= DataReceived;
sensor.StopListening();

return;

void DataReceived(object sender, SensorDataEventArgs<Tuple<double, double, double>> e)
{
    Console.WriteLine("Nadmořská výška (m): " + e.Value.Item1);
    Console.WriteLine("Atmosférický tlak (atm): " + e.Value.Item2);
    Console.WriteLine("Teplota (°C): " + e.Value.Item3);
}