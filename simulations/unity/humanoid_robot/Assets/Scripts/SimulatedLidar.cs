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