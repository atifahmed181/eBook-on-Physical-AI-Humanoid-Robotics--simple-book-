---
sidebar_position: 2
---

# Physics Simulation in Gazebo: Gravity, Collisions, and Environment Building

## Introduction to Gazebo

Gazebo is a powerful open-source physics simulator that provides realistic simulation of robots in complex indoor and outdoor environments. For humanoid robotics, Gazebo is invaluable for testing algorithms in a safe environment before deployment on physical robots.

## Core Concepts

### Physics Engine
Gazebo uses Open Dynamics Engine (ODE), Bullet, or DART as its underlying physics engine. These engines handle:
- Collision detection
- Rigid body dynamics
- Joint constraints
- Friction and contact simulation

### Worlds and Environments
In Gazebo, a "world" is a collection of models, lights, and environmental settings. Worlds are defined in `.world` files using the SDF (Simulation Description Format).

## Setting up Gazebo for Humanoid Simulation

### Installing Gazebo
Most ROS 2 distributions come with Gazebo integration. For standalone installation:

```bash
# On Ubuntu
sudo apt install gazebo libgazebo-dev

# For ROS 2 integration
sudo apt install ros-<ros2-distro>-gazebo-ros-pkgs
```

### Basic Gazebo Launch

```xml
<!-- launch_gazebo.launch.py -->
from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # Launch Gazebo
        ExecuteProcess(
            cmd=['gazebo', '--verbose', '-slibgazebo_ros_init.so', '-slibgazebo_ros_factory.so'],
            output='screen'
        ),
    ])
```

## Creating a Humanoid World

Here's an example world file that sets up a basic environment for humanoid simulation:

```xml
<?xml version="1.0" ?>
<sdf version="1.6">
  <world name="humanoid_world">
    <!-- Include the default ground plane -->
    <include>
      <uri>model://ground_plane</uri>
    </include>

    <!-- Include the default light source -->
    <include>
      <uri>model://sun</uri>
    </include>

    <!-- Custom environment elements -->
    <model name='table'>
      <pose>1 0 0.5 0 0 0</pose>
      <link name='table_link'>
        <visual name='visual'>
          <geometry>
            <box>
              <size>1 1 0.02</size>
            </box>
          </geometry>
        </visual>
        <collision name='collision'>
          <geometry>
            <box>
              <size>1 1 0.02</size>
            </box>
          </geometry>
        </collision>
        <inertial>
          <mass>10.0</mass>
          <inertia>
            <ixx>1.0</ixx>
            <ixy>0.0</ixy>
            <ixz>0.0</ixz>
            <iyy>1.0</iyy>
            <iyz>0.0</iyz>
            <izz>1.0</izz>
          </inertia>
        </inertial>
      </link>
    </model>

    <!-- Add obstacles for navigation testing -->
    <model name='obstacle1'>
      <pose>-1 1 0.5 0 0 0</pose>
      <link name='link'>
        <visual name='visual'>
          <geometry>
            <cylinder>
              <radius>0.2</radius>
              <length>1.0</length>
            </cylinder>
          </geometry>
        </visual>
        <collision name='collision'>
          <geometry>
            <cylinder>
              <radius>0.2</radius>
              <length>1.0</length>
            </cylinder>
          </geometry>
        </collision>
        <inertial>
          <mass>5.0</mass>
          <inertia>
            <ixx>1.0</ixx>
            <ixy>0.0</ixy>
            <ixz>0.0</ixz>
            <iyy>1.0</iyy>
            <iyz>0.0</iyz>
            <izz>1.0</izz>
          </inertia>
        </inertial>
      </link>
    </model>
  </world>
</sdf>
```

## Physics Parameters and Tuning

### Gravity
By default, Gazebo simulates Earth's gravity (9.81 m/s²), but you can adjust it:

```xml
<world name="custom_gravity_world">
  <gravity>0 0 -4.9</gravity>  <!-- Half of Earth's gravity -->
  <!-- ... rest of the world definition ... -->
</world>
```

### Damping and Friction
Fine-tune the physical properties of your models:

```xml
<model name="humanoid_robot">
  <!-- ... other model elements ... -->
  <link name="foot">
    <collision name="collision">
      <surface>
        <friction>
          <ode>
            <mu>0.8</mu>
            <mu2>0.8</mu2>
          </ode>
        </friction>
        <bounce>
          <restitution_coefficient>0.01</restitution_coefficient>
          <threshold>100000</threshold>
        </bounce>
        <contact>
          <ode>
            <kp>1e+16</kp>
            <kd>1</kd>
            <max_vel>100.0</max_vel>
            <min_depth>0.001</min_depth>
          </ode>
        </contact>
      </surface>
    </collision>
  </link>
</model>
```

## Collision Detection

Gazebo uses ODE, Bullet, or DART for collision detection. You can specify different collision properties for different parts of your robot:

```xml
<link name="humanoid_link">
  <!-- Visual properties (what you see) -->
  <visual name="visual">
    <geometry>
      <mesh filename="humanoid_link.dae" />
    </geometry>
  </visual>
  
  <!-- Collision properties (physics interactions) -->
  <collision name="collision">
    <geometry>
      <!-- Often use simplified geometry for collision to improve performance -->
      <box size="0.1 0.1 0.3" />
    </geometry>
  </collision>
</link>
```

## Integrating with ROS 2

Gazebo ROS 2 packages provide bridges between Gazebo and ROS 2:

```xml
<!-- In your URDF/SDF for Gazebo integration -->
<gazebo>
  <plugin name="gazebo_ros_control" filename="libgazebo_ros_control.so">
    <robotNamespace>/humanoid_robot</robotNamespace>
  </plugin>
</gazebo>
```

## Practical Exercise

Create a Gazebo world file that includes:
- A humanoid robot model 
- A flat ground plane with realistic friction
- Several obstacles of different shapes and sizes
- Different lighting conditions
- Physics parameters tuned for humanoid robot simulation

## Advanced Physics Considerations

### Real-time Factor
Control how fast or slow the simulation runs:

```bash
gazebo --playback-rate=0.5  # Run at half speed
```

### Performance vs. Accuracy
Balance physics accuracy with simulation speed:
- Lower step size: More accurate but slower
- Higher solver iterations: More stable but slower
- Simplified collision meshes: Faster but less accurate

## Key Takeaways

- Gazebo provides realistic physics simulation essential for humanoid robot development
- Proper collision detection and physics parameters are crucial for accurate simulation
- World files allow for complex environment creation
- Integration with ROS 2 enables seamless simulation-to-reality transfer
- Careful tuning of physics parameters is necessary for humanoid robots