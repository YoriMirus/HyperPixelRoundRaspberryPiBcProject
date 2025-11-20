namespace CommunicationLibrary.I2CSensors.DTOs;

public struct AccelerometerDTO
{
    public double AccelerationX;
    public double AccelerationY;
    public double AccelerationZ;

    public AccelerometerDTO(double x, double y, double z)
    {
        AccelerationX = x;
        AccelerationY = y;
        AccelerationZ = z;
    }
}