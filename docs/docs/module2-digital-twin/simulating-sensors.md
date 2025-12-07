---
sidebar_position: 4
---

# Simulating Sensors: LiDAR, Depth Cameras, and IMUs

## Introduction to Sensor Simulation

Sensors are the eyes and ears of humanoid robots, providing crucial data about the environment and the robot's state. In simulation, accurately modeling these sensors is essential for developing robust perception and navigation algorithms that can later be deployed on real hardware.

This chapter covers the simulation of three critical sensor types for humanoid robotics:
- LiDAR (Light Detection and Ranging) for 2D/3D mapping and navigation
- Depth Cameras for 3D perception and obstacle detection
- IMUs (Inertial Measurement Units) for orientation and motion tracking

## LiDAR Simulation

### Understanding LiDAR
LiDAR sensors emit laser beams and measure the time it takes for the light to return after hitting an object. This creates precise distance measurements in a 2D or 3D scan pattern.

### LiDAR in Gazebo
In Gazebo, LiDAR sensors are modeled using the `<sensor>` tag in SDF/URDF files:

```xml
<link name="lidar_link">
  <visual>
    <geometry>
      <cylinder radius="0.05" length="0.05"/>
    </geometry>
  </visual>
  <collision>
    <geometry>
      <cylinder radius="0.05" length="0.05"/>
    </geometry>
  </collision>
  
  <sensor name="lidar" type="ray">
    <always_on>true</always_on>
    <update_rate>10</update_rate>
    <ray>
      <scan>
        <horizontal>
          <samples>720</samples>
          <resolution>1</resolution>
          <min_angle>-1.570796</min_angle>  <!-- -90 degrees -->
          <max_angle>1.570796</max_angle>   <!-- 90 degrees -->
        </horizontal>
      </scan>
      <range>
        <min>0.1</min>
        <max>30.0</max>
        <resolution>0.01</resolution>
      </range>
    </ray>
    <plugin name="lidar_controller" filename="libgazebo_ros_ray_sensor.so">
      <ros>
        <namespace>humanoid_robot</namespace>
        <remapping>~/out:=scan</remapping>
      </ros>
      <output_type>sensor_msgs/LaserScan</output_type>
    </plugin>
  </sensor>
</link>
```

### LiDAR in Unity
For Unity, we can create a simulated LiDAR using raycasting:

```csharp
using UnityEngine;
using System.Collections.Generic;

public class SimulatedLidar : MonoBehaviour
{
    [Header("Lidar Configuration")]
    public int horizontalRays = 360;
    public int verticalRays = 1;  // For 2D lidar, use 1
    public float maxRange = 10.0f;
    public float minAngle = -90f;
    public float maxAngle = 90f;

    [Header("Output Settings")]
    public string topicName = "/scan";
    
    private List<float> ranges;
    private float angleIncrement;

    void Start()
    {
        ranges = new List<float>(new float[horizontalRays]);
        angleIncrement = (maxAngle - minAngle) / horizontalRays;
    }

    void Update()
    {
        // Update lidar scan each frame
        UpdateLidarScan();
    }

    void UpdateLidarScan()
    {
        for (int i = 0; i < horizontalRays; i++)
        {
            float angle = minAngle + (i * angleIncrement);
            float radAngle = angle * Mathf.Deg2Rad;

            // Calculate direction vector based on robot's orientation
            Vector3 direction = new Vector3(
                Mathf.Cos(radAngle) * transform.right.x + Mathf.Sin(radAngle) * transform.forward.x,
                0,
                Mathf.Cos(radAngle) * transform.right.z + Mathf.Sin(radAngle) * transform.forward.z
            );

            // Perform raycast to detect obstacles
            RaycastHit hit;
            if (Physics.Raycast(transform.position, direction, out hit, maxRange))
            {
                ranges[i] = hit.distance;
            }
            else
            {
                ranges[i] = maxRange;
            }
        }
    }

    public float[] GetLidarData()
    {
        return ranges.ToArray();
    }

    // Visualization in editor
    void OnDrawGizmos()
    {
        if (ranges == null) return;

        for (int i = 0; i < horizontalRays; i += 10)  // Show every 10th ray to avoid clutter
        {
            float angle = minAngle + (i * angleIncrement);
            float radAngle = angle * Mathf.Deg2Rad;

            Vector3 direction = new Vector3(
                Mathf.Cos(radAngle) * transform.right.x + Mathf.Sin(radAngle) * transform.forward.x,
                0,
                Mathf.Cos(radAngle) * transform.right.z + Mathf.Sin(radAngle) * transform.forward.z
            );

            Vector3 endPos = transform.position + direction * ranges[i];
            Gizmos.color = ranges[i] < maxRange ? Color.red : Color.green;
            Gizmos.DrawLine(transform.position, endPos);
        }
    }
}
```

## Depth Camera Simulation

### Understanding Depth Cameras
Depth cameras provide distance measurements to objects in the scene for each pixel, creating a 2D array of distance values. This is crucial for 3D scene understanding.

### Depth Camera in Gazebo
```xml
<sensor name="depth_camera" type="depth">
  <always_on>true</always_on>
  <update_rate>30</update_rate>
  <camera name="depth_cam">
    <horizontal_fov>1.047</horizontal_fov>  <!-- ~60 degrees -->
    <image>
      <format>R8G8B8</format>
      <width>640</width>
      <height>480</height>
    </image>
    <clip>
      <near>0.1</near>
      <far>10</far>
    </clip>
  </camera>
  <plugin name="depth_camera_controller" filename="libgazebo_ros_openni_kinect.so">
    <alwaysOn>true</alwaysOn>
    <updateRate>30.0</updateRate>
    <cameraName>depth_camera</cameraName>
    <imageTopicName>/depth_camera/image_raw</imageTopicName>
    <depthImageTopicName>/depth_camera/depth/image_raw</depthImageTopicName>
    <pointCloudTopicName>/depth_camera/depth/points</pointCloudTopicName>
    <frameName>depth_camera_frame</frameName>
  </plugin>
</sensor>
```

### Depth Camera in Unity
```csharp
using UnityEngine;
using System.Collections;

public class SimulatedDepthCamera : MonoBehaviour
{
    [Header("Camera Settings")]
    public Camera depthCamera;
    public int width = 640;
    public int height = 480;
    public float maxDepth = 10.0f;

    private RenderTexture depthTexture;
    private Texture2D readTexture;
    private float[] depthData;

    void Start()
    {
        // Create render texture for depth data
        depthTexture = new RenderTexture(width, height, 24, RenderTextureFormat.RFloat);
        depthTexture.Create();

        readTexture = new Texture2D(width, height, TextureFormat.RFloat, false);
        
        // Configure camera to render to our texture
        depthCamera.targetTexture = depthTexture;
        
        // Initialize depth data array
        depthData = new float[width * height];
    }

    void Update()
    {
        // Capture depth frame
        CaptureDepthFrame();
    }

    void CaptureDepthFrame()
    {
        // Set the render texture to active
        RenderTexture.active = depthTexture;

        // Read the rendered texture
        readTexture.ReadPixels(new Rect(0, 0, width, height), 0, 0);
        readTexture.Apply();

        // Extract depth data from texture
        Color[] colors = readTexture.GetPixels();
        for (int i = 0; i < colors.Length; i++)
        {
            // Depth value is stored in the red channel
            depthData[i] = colors[i].r * maxDepth;
        }

        RenderTexture.active = null;
    }

    public float[] GetDepthData()
    {
        return depthData;
    }

    public float GetDepthAt(int x, int y)
    {
        if (x >= 0 && x < width && y >= 0 && y < height)
        {
            return depthData[y * width + x];
        }
        return maxDepth;  // Return max depth if out of bounds
    }
}
```

## IMU Simulation

### Understanding IMUs
IMUs measure linear acceleration and angular velocity. Many include magnetometers for absolute orientation. For humanoid robots, IMUs are essential for balance control and motion detection.

### IMU in Gazebo
```xml
<sensor name="imu_sensor" type="imu">
  <always_on>true</always_on>
  <update_rate>100</update_rate>
  <imu>
    <angular_velocity>
      <x>
        <noise type="gaussian">
          <mean>0.0</mean>
          <stddev>0.0017</stddev>
        </noise>
      </x>
      <y>
        <noise type="gaussian">
          <mean>0.0</mean>
          <stddev>0.0017</stddev>
        </noise>
      </y>
      <z>
        <noise type="gaussian">
          <mean>0.0</mean>
          <stddev>0.0017</stddev>
        </noise>
      </z>
    </angular_velocity>
    <linear_acceleration>
      <x>
        <noise type="gaussian">
          <mean>0.0</mean>
          <stddev>1.7e-04</stddev>
        </noise>
      </x>
      <y>
        <noise type="gaussian">
          <mean>0.0</mean>
          <stddev>1.7e-04</stddev>
        </noise>
      </y>
      <z>
        <noise type="gaussian">
          <mean>0.0</mean>
          <stddev>1.7e-04</stddev>
        </noise>
      </z>
    </linear_acceleration>
  </imu>
  <plugin name="imu_plugin" filename="libgazebo_ros_imu.so">
    <ros>
      <namespace>humanoid_robot</namespace>
      <remapping>~/out:=imu</remapping>
    </ros>
    <initial_orientation_as_reference>false</initial_orientation_as_reference>
  </plugin>
</sensor>
```

### IMU Simulation in Unity
```csharp
using UnityEngine;

public class SimulatedIMU : MonoBehaviour
{
    [Header("IMU Configuration")]
    public float noiseLevel = 0.01f;
    public Transform robotBody;

    private Vector3 trueAcceleration;
    private Vector3 trueAngularVelocity;
    private Vector3 lastPosition;
    private Quaternion lastRotation;
    private float lastTime;

    void Start()
    {
        lastPosition = robotBody.position;
        lastRotation = robotBody.rotation;
        lastTime = Time.time;
    }

    void Update()
    {
        UpdateIMUReadings();
    }

    void UpdateIMUReadings()
    {
        float deltaTime = Time.time - lastTime;
        if (deltaTime <= 0) return;

        // Calculate true acceleration (linear)
        Vector3 currentPosition = robotBody.position;
        Vector3 currentVelocity = (currentPosition - lastPosition) / deltaTime;
        trueAcceleration = (currentVelocity - (currentPosition - lastPosition) / deltaTime) / deltaTime;

        // Calculate true angular velocity
        Quaternion currentRotation = robotBody.rotation;
        Quaternion rotationDiff = currentRotation * Quaternion.Inverse(lastRotation);
        Vector3 angularVelocity = new Vector3(
            Mathf.Atan2(rotationDiff.z, rotationDiff.w) * 2.0f / deltaTime,
            Mathf.Atan2(rotationDiff.y, rotationDiff.w) * 2.0f / deltaTime,
            Mathf.Atan2(rotationDiff.x, rotationDiff.w) * 2.0f / deltaTime
        );

        lastPosition = currentPosition;
        lastRotation = currentRotation;
        lastTime = Time.time;
    }

    public Vector3 GetLinearAcceleration()
    {
        // Add noise to simulate real IMU
        Vector3 noise = new Vector3(
            Random.Range(-noiseLevel, noiseLevel),
            Random.Range(-noiseLevel, noiseLevel),
            Random.Range(-noiseLevel, noiseLevel)
        );
        return trueAcceleration + noise;
    }

    public Vector3 GetAngularVelocity()
    {
        // Add noise to simulate real IMU
        Vector3 noise = new Vector3(
            Random.Range(-noiseLevel, noiseLevel),
            Random.Range(-noiseLevel, noiseLevel),
            Random.Range(-noiseLevel, noiseLevel)
        );
        return trueAngularVelocity + noise;
    }

    public Quaternion GetOrientation()
    {
        return robotBody.rotation;
    }
}
```

## Sensor Fusion in Simulation

Simulating how multiple sensors work together:

```csharp
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
```

## Accuracy Considerations

### Noise Modeling
Real sensors have noise and inaccuracies that should be simulated:

```csharp
// Noise generation for realistic sensor simulation
public class SensorNoise
{
    public static float AddGaussianNoise(float value, float mean, float stddev)
    {
        // Box-Muller transform for Gaussian distribution
        float u1 = 1.0f - Random.value; // Uniform(0,1] random doubles
        float u2 = 1.0f - Random.value;
        float randStdNormal = Mathf.Sqrt(-2.0f * Mathf.Log(u1)) * Mathf.Sin(2.0f * Mathf.PI * u2); // Random normal(0,1)
        float randNormal = mean + stddev * randStdNormal; // Random normal(mean,stdDev^2)

        return value + randNormal;
    }

    public static float AddUniformNoise(float value, float noiseRange)
    {
        float noise = Random.Range(-noiseRange, noiseRange);
        return value + noise;
    }

    public static float AddBias(float value, float bias)
    {
        return value + bias;
    }
}
```

## Practical Exercise

Create a Unity scene with:
- A humanoid robot model
- Simulated LiDAR, depth camera, and IMU
- A simple environment with obstacles
- Visualization of sensor data
- A display showing fused sensor information

## Key Takeaways

- Accurate sensor simulation is crucial for developing robust robotics algorithms
- LiDAR, depth cameras, and IMUs each provide unique information about the environment
- Noise and imperfections should be modeled in simulation for realistic results
- Sensor fusion techniques combine data from multiple sensors for better accuracy
- Both Gazebo and Unity provide tools for different types of sensor simulation