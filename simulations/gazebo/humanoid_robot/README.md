# Gazebo Humanoid Robot Simulation

This directory contains a basic simulation setup for a humanoid robot in Gazebo.

## Directory Structure

```
gazebo/humanoid_robot/
├── humanoid_world.world      # Gazebo world file with environment and robot
├── simple_humanoid.urdf      # URDF model of the humanoid robot
├── launch_humanoid.launch    # Launch file to start the simulation
└── README.md                 # This file
```

## Overview

This basic humanoid simulation includes:
- A simplified humanoid model with torso, head, and arms
- A world with basic obstacles for navigation testing
- Physics properties configured for realistic simulation

## Running the Simulation

To run this simulation, you need to have ROS 2 and Gazebo installed with the necessary ROS packages:

1. Source your ROS 2 environment:
```bash
source /opt/ros/<ros2-distro>/setup.bash
```

2. Navigate to this directory and launch the simulation:
```bash
# Using the launch file directly (if properly configured)
ros2 launch launch_humanoid.launch
```

Alternatively, you can run Gazebo directly with the world file:
```bash
gazebo worlds/humanoid_world.world
```

## Components

### World File
The `humanoid_world.world` file contains:
- A ground plane
- A simple humanoid robot model
- Basic obstacles (table and box)

### URDF Model
The `simple_humanoid.urdf` file defines the robot with:
- Torso link (body)
- Head link
- Left and right arm links with joints
- Basic physical properties

### Launch File
The `launch_humanoid.launch` file provides a convenient way to:
- Start Gazebo with the specific world
- Spawn the robot model in the simulation
- Load the robot description

## Extending the Simulation

To enhance this simulation:
1. Add more complex robot models with additional joints
2. Create more detailed environments
3. Add sensors (LiDAR, cameras, IMUs) to the robot
4. Implement control interfaces for robot movement
5. Add more complex obstacles and navigation challenges