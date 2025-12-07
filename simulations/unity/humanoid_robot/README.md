# Unity Humanoid Robot Simulation

This directory contains a basic Unity project structure for simulating a humanoid robot with high-fidelity rendering and sensor simulation.

## Directory Structure

```
unity/humanoid_robot/
├── Assets/                   # Unity assets folder
│   ├── Models/              # 3D models for the robot and environment
│   ├── Scripts/             # C# scripts for robot control and simulation
│   │   ├── HumanoidRobotController.cs    # Main robot movement controller
│   │   ├── SimulatedLidar.cs             # LiDAR sensor simulation
│   │   ├── SimulatedDepthCamera.cs       # Depth camera simulation
│   │   ├── SimulatedIMU.cs               # IMU sensor simulation
│   │   └── SensorFusion.cs               # Sensor data fusion
│   ├── Scenes/              # Unity scene files
│   │   └── SampleScene.unity # Basic scene with robot and environment
│   ├── Prefabs/             # Reusable game object templates
│   └── Materials/           # Material definitions for 3D objects
├── Packages/                # Unity package management
│   └── manifest.json        # Package dependencies
└── README.md                # This file
```

## Overview

This Unity project includes:
- Basic humanoid robot controller with movement and animation
- Sensor simulation (LiDAR, depth camera, IMU)
- Sensor fusion algorithms
- Sample scene setup

## Getting Started

To use this Unity project:

1. Open Unity Hub
2. Click "Add" and navigate to this directory (`unity/humanoid_robot`)
3. Unity will detect the project and allow you to open it

Or if opening from Unity directly:
1. Select "Open" from the Unity Hub
2. Navigate to the `simulations/unity/humanoid_robot` directory
3. Click "Open"

## Key Scripts

### HumanoidRobotController.cs
- Basic movement controls for the humanoid robot
- Input handling for keyboard/gamepad
- Animation integration

### SimulatedLidar.cs
- Simulates 2D/3D LiDAR sensors
- Uses Unity's physics raycasting
- Configurable parameters (range, resolution, etc.)

### SimulatedDepthCamera.cs
- Simulates RGB-D camera depth perception
- Uses RenderTexture to capture depth information
- Returns depth data array for processing

### SimulatedIMU.cs
- Simulates Inertial Measurement Unit data
- Tracks acceleration and rotation
- Includes realistic noise modeling

### SensorFusion.cs
- Combines data from multiple sensors
- Implements basic fusion algorithms
- Provides integrated sensor output

## Extending the Simulation

To enhance this simulation:
1. Add more complex robot models
2. Create detailed environments with realistic lighting
3. Implement more sophisticated sensor models
4. Add ROS# integration for ROS communication
5. Create more advanced AI behaviors

## Prerequisites

- Unity 2021.3 LTS or newer
- Basic knowledge of C# and Unity development
- Understanding of robotics concepts (optional but helpful)