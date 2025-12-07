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