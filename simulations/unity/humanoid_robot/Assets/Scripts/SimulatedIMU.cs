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