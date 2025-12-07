using UnityEngine;
using System.Collections.Generic;

public class SensorFusion : MonoBehaviour
{
    public SimulatedLidar lidar;
    public SimulatedDepthCamera depthCamera;
    public SimulatedIMU imu;

    private List<float> fusedData;

    void Start()
    {
        fusedData = new List<float>();
    }

    void Update()
    {
        // Integrate data from all sensors
        float[] lidarData = lidar.GetLidarData();
        float[] depthData = depthCamera.GetDepthData();
        Vector3 imuAccel = imu.GetLinearAcceleration();
        Vector3 imuGyro = imu.GetAngularVelocity();

        // Example fusion: combine lidar and IMU for better obstacle detection
        FusedObstacleDetection(lidarData, imuAccel);
    }

    void FusedObstacleDetection(float[] lidarData, Vector3 imuAccel)
    {
        // When IMU detects rapid movement, be more conservative with lidar readings
        float movementThreshold = 2.0f;
        if (imuAccel.magnitude > movementThreshold)
        {
            // Consider IMU data to validate lidar readings
            Debug.Log("Robot is moving rapidly, cross-referencing sensor data");
        }
    }

    public void PublishFusedData()
    {
        // This would publish to ROS topics in a real implementation
        // ros.Publish("sensor_fusion", fusedData);
    }
}