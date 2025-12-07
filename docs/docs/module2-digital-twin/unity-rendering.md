---
sidebar_position: 3
---

# High-Fidelity Rendering and Human-Robot Interaction in Unity

## Introduction to Unity for Robotics

Unity is a powerful 3D development platform that excels at creating visually impressive and interactive environments. While Gazebo focuses on physics simulation, Unity is ideal for high-fidelity rendering and creating immersive human-robot interaction scenarios. For humanoid robotics, Unity provides exceptional visual quality and user experience.

## Unity Robotics Setup

### Installing Unity
To get started with robotics in Unity:
1. Download and install Unity Hub
2. Install Unity 2021.3 LTS or later
3. Install the Unity Robotics Hub package

### Unity Robotics Package
The Unity Robotics Package provides:
- ROS# communication bridge
- Robot control interfaces
- Sample scenes and tutorials

```csharp
// Example of Unity ROS communication
using Unity.Robotics.ROSTCPConnector;
using RosMessageTypes.Std;

// Connect to ROS network
ROSTCPConnector ros = ROSTCPConnector.instance;
ros.InitializeROSTCPConnector("127.0.0.1", 10000);

// Publish a message
StringMsg msg = new StringMsg("Hello from Unity!");
ros.Publish("unity_topic", msg);
```

## Creating High-Fidelity Environments

### Terrain and Environment Creation
Unity's terrain system allows for creating realistic outdoor environments:

```csharp
// Example: Programmatically adjusting terrain
public class TerrainController : MonoBehaviour
{
    public Terrain terrain;
    public float brushRadius = 5.0f;
    public float brushStrength = 0.5f;

    void Update()
    {
        if (Input.GetMouseButton(0))  // Left mouse button
        {
            Vector3 mousePos = Input.mousePosition;
            Vector3 worldPos = Camera.main.ScreenToWorldPoint(
                new Vector3(mousePos.x, mousePos.y, Camera.main.nearClipPlane));
            
            SmoothTerrain(worldPos);
        }
    }

    void SmoothTerrain(Vector3 worldPos)
    {
        TerrainData terrainData = terrain.terrainData;
        Vector3 terrainPos = worldPos - terrain.transform.position;
        
        int mapX = (int)((terrainPos.x / terrainData.size.x) * terrainData.heightmapResolution);
        int mapZ = (int)((terrainPos.z / terrainData.size.z) * terrainData.heightmapResolution);
        
        // Apply smoothing effect to terrain
        float[,] heights = terrainData.GetHeights(mapX - (int)brushRadius, mapZ - (int)brushRadius, 
            (int)(brushRadius * 2), (int)(brushRadius * 2));
        
        // Apply smoothing algorithm to heights...
    }
}
```

### Material and Lighting
High-quality visuals require attention to materials and lighting:

```csharp
// Dynamic lighting to simulate different times of day
public class DynamicLighting : MonoBehaviour
{
    public Light sunLight;
    public Gradient skyGradient;
    public float dayCycleSpeed = 0.5f;
    
    void Update()
    {
        // Rotate the sun to simulate day cycle
        float rotation = (Time.time * dayCycleSpeed) % 360;
        sunLight.transform.rotation = Quaternion.Euler(rotation, 0, 0);
        
        // Adjust sky color based on sun position
        RenderSettings.skybox.SetColor("_Tint", skyGradient.Evaluate(rotation / 360));
    }
}
```

## Humanoid Robot Modeling in Unity

### Importing Robot Models
For humanoid robots, import your URDF model or create directly in Unity:

```csharp
// Sample humanoid robot controller in Unity
using UnityEngine;

public class HumanoidRobotController : MonoBehaviour
{
    public Animator animator;
    public float moveSpeed = 2.0f;
    public float turnSpeed = 100.0f;
    public Transform robotRoot;

    void Update()
    {
        HandleMovement();
        HandleAnimations();
    }

    void HandleMovement()
    {
        float horizontal = Input.GetAxis("Horizontal");
        float vertical = Input.GetAxis("Vertical");
        
        Vector3 movement = new Vector3(horizontal, 0, vertical) * moveSpeed * Time.deltaTime;
        robotRoot.Translate(movement);
        
        if (horizontal != 0 || vertical != 0)
        {
            // Turn robot to face movement direction
            Vector3 targetDirection = new Vector3(horizontal, 0, vertical);
            Quaternion targetRotation = Quaternion.LookRotation(targetDirection);
            robotRoot.rotation = 
                Quaternion.RotateTowards(robotRoot.rotation, targetRotation, turnSpeed * Time.deltaTime);
        }
    }

    void HandleAnimations()
    {
        float horizontal = Input.GetAxis("Horizontal");
        float vertical = Input.GetAxis("Vertical");
        
        // Blend walking/running animations based on movement
        if (vertical > 0.1f)
        {
            animator.SetFloat("Speed", vertical);
        }
        else
        {
            animator.SetFloat("Speed", 0);
        }
    }
}
```

## Sensor Simulation in Unity

Unity can simulate various sensors that humanoid robots use:

### Depth Camera Simulation
```csharp
// Depth camera simulation
using UnityEngine;

public class DepthCamera : MonoBehaviour
{
    public Camera cam;
    public Shader depthShader;
    private RenderTexture depthTexture;
    private Material depthMaterial;

    void Start()
    {
        // Create depth texture
        depthTexture = new RenderTexture(640, 480, 24, RenderTextureFormat.RFloat);
        depthMaterial = new Material(depthShader);
        
        cam.targetTexture = depthTexture;
    }

    void OnRenderImage(RenderTexture source, RenderTexture destination)
    {
        // Apply depth effect
        Graphics.Blit(source, destination, depthMaterial);
    }

    // Function to read depth data
    public float[] GetDepthData()
    {
        RenderTexture.active = depthTexture;
        Texture2D tex = new Texture2D(depthTexture.width, depthTexture.height, TextureFormat.RFloat, false);
        tex.ReadPixels(new Rect(0, 0, depthTexture.width, depthTexture.height), 0, 0);
        tex.Apply();
        
        Color[] colors = tex.GetPixels();
        float[] depths = new float[colors.Length];
        for (int i = 0; i < colors.Length; i++)
        {
            depths[i] = colors[i].r;  // Depth stored in red channel
        }
        
        DestroyImmediate(tex);
        RenderTexture.active = null;
        
        return depths;
    }
}
```

### LiDAR Simulation
```csharp
// LiDAR simulation
using UnityEngine;
using System.Collections.Generic;

public class LiDARSimulation : MonoBehaviour
{
    public int numRays = 360;
    public float maxDistance = 10.0f;
    public float fieldOfView = 360.0f;
    public Transform lidarOrigin;

    public List<float> Scan()
    {
        List<float> distances = new List<float>();

        for (int i = 0; i < numRays; i++)
        {
            float angle = (i * fieldOfView / numRays) * Mathf.Deg2Rad;
            Vector3 direction = new Vector3(Mathf.Cos(angle), 0, Mathf.Sin(angle));
            
            Ray ray = new Ray(lidarOrigin.position, direction);
            RaycastHit hit;
            
            if (Physics.Raycast(ray, out hit, maxDistance))
            {
                distances.Add(hit.distance);
            }
            else
            {
                distances.Add(maxDistance);  // No obstacle detected
            }
        }

        return distances;
    }

    // Visualization of LiDAR scan
    void OnDrawGizmos()
    {
        if (lidarOrigin != null)
        {
            for (int i = 0; i < numRays; i += 10)  // Draw every 10th ray for visibility
            {
                float angle = (i * fieldOfView / numRays) * Mathf.Deg2Rad;
                Vector3 direction = new Vector3(Mathf.Cos(angle), 0, Mathf.Sin(angle));
                
                Ray ray = new Ray(lidarOrigin.position, direction);
                
                RaycastHit hit;
                if (Physics.Raycast(ray, out hit, maxDistance))
                {
                    Gizmos.color = Color.red;
                    Gizmos.DrawLine(ray.origin, hit.point);
                }
                else
                {
                    Gizmos.color = Color.green;
                    Gizmos.DrawLine(ray.origin, ray.origin + direction * maxDistance);
                }
            }
        }
    }
}
```

## Human-Robot Interaction

Creating intuitive human-robot interaction interfaces:

```csharp
// Human-Robot Interaction System
using UnityEngine;
using UnityEngine.UI;
using System.Collections;

public class HumanRobotInteraction : MonoBehaviour
{
    public GameObject robot;
    public Button followMeButton;
    public Button stopButton;
    public Text statusText;
    
    private bool following = false;

    void Start()
    {
        followMeButton.onClick.AddListener(StartFollowing);
        stopButton.onClick.AddListener(StopFollowing);
    }

    void StartFollowing()
    {
        following = true;
        StartCoroutine(FollowRoutine());
        statusText.text = "Robot is following";
    }

    void StopFollowing()
    {
        following = false;
        statusText.text = "Robot stopped";
    }

    IEnumerator FollowRoutine()
    {
        while (following)
        {
            // Move robot towards player
            Vector3 direction = (transform.position - robot.transform.position).normalized;
            direction.y = 0;  // Only follow in 2D
            
            robot.transform.position += direction * 0.1f;
            
            // Update robot's facing direction
            robot.transform.LookAt(transform);
            
            yield return new WaitForSeconds(0.1f);
        }
    }
}
```

## Integration with ROS 2

### ROS Communication in Unity
```csharp
// Example ROS communication from Unity
using Unity.Robotics.ROSTCPConnector;
using RosMessageTypes.Sensor;
using RosMessageTypes.Geometry;

public class UnityRobotController : MonoBehaviour
{
    ROSTCPConnector ros;
    string robotNamespace = "/unity_humanoid_robot";
    
    void Start()
    {
        ros = ROSTCPConnector.instance;
        
        // Subscribe to robot commands
        ros.Subscribe<GeometryMsgsTwist>(robotNamespace + "/cmd_vel", ReceiveCommand);
    }
    
    void ReceiveCommand(GeometryMsgsTwist cmd)
    {
        // Convert ROS Twist message to Unity movement
        Vector3 linear = new Vector3((float)cmd.linear.x, (float)cmd.linear.y, (float)cmd.linear.z);
        Vector3 angular = new Vector3((float)cmd.angular.x, (float)cmd.angular.y, (float)cmd.angular.z);
        
        // Apply movement to robot
        transform.Translate(linear * Time.deltaTime);
        transform.Rotate(angular * Mathf.Rad2Deg * Time.deltaTime);
    }
}
```

## Performance Optimization

For complex humanoid robot simulations:

### Level of Detail (LOD)
```csharp
// LOD system for humanoid robot
using UnityEngine;

public class HumanoidLOD : MonoBehaviour
{
    public Renderer[] lodRenderers;
    public float[] lodDistances = {5f, 15f, 30f};
    
    void Update()
    {
        float distance = Vector3.Distance(Camera.main.transform.position, transform.position);
        
        for (int i = 0; i < lodRenderers.Length; i++)
        {
            if (distance < lodDistances[i])
            {
                lodRenderers[i].enabled = true;
            }
            else
            {
                lodRenderers[i].enabled = false;
            }
        }
    }
}
```

## Practical Exercise

Create a Unity scene that includes:
- A humanoid robot with realistic animations
- High-fidelity environment with realistic lighting
- Depth camera simulation
- LiDAR simulation
- Simple human-robot interaction interface
- ROS communication bridge

## Key Takeaways

- Unity excels at high-fidelity rendering and visual quality
- Sensor simulation in Unity provides realistic data for AI training
- Human-robot interaction interfaces enhance the development experience
- ROS integration allows seamless communication with other robotics software
- Performance optimization is crucial for complex humanoid simulations