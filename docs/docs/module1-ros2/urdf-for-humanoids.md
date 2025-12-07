---
sidebar_position: 4
---

# Understanding URDF for Humanoid Robots

## Introduction to URDF

URDF (Unified Robot Description Format) is an XML-based format used in ROS to describe robot models, including their kinematic and dynamic properties. For humanoid robots, URDF becomes especially important as it defines the complex structure of limbs, joints, and sensors that make up these anthropomorphic machines.

## URDF Fundamentals

URDF describes a robot as a collection of links connected by joints. Each link contains information about its visual representation, collision properties, and inertial characteristics, while joints define the allowed motion between links.

### Basic URDF Elements

- **Links**: Rigid bodies with visual and collision properties
- **Joints**: Connections between links that allow relative motion 
- **Materials**: Visual appearance definitions
- **Transmissions**: Actuator interface definitions
- **Gazebo**: Simulation-specific extensions

## Basic URDF Structure for Humanoids

Let's look at an example URDF for a simplified humanoid robot:

```xml
<?xml version="1.0"?>
<robot name="simple_humanoid">
  
  <!-- Base Link -->
  <link name="base_link">
    <visual>
      <geometry>
        <box size="0.3 0.2 0.1"/>
      </geometry>
      <material name="blue">
        <color rgba="0 0 1 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <box size="0.3 0.2 0.1"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="10.0"/>
      <inertia ixx="0.1" ixy="0" ixz="0" iyy="0.2" iyz="0" izz="0.3"/>
    </inertial>
  </link>

  <!-- Torso -->
  <link name="torso">
    <visual>
      <geometry>
        <box size="0.2 0.1 0.4"/>
      </geometry>
      <origin xyz="0 0 0.25"/>
      <material name="grey">
        <color rgba="0.5 0.5 0.5 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <box size="0.2 0.1 0.4"/>
      </geometry>
      <origin xyz="0 0 0.25"/>
    </collision>
    <inertial>
      <mass value="5.0"/>
      <inertia ixx="0.05" ixy="0" ixz="0" iyy="0.1" iyz="0" izz="0.15"/>
    </inertial>
  </link>

  <!-- Joint connecting base to torso -->
  <joint name="base_to_torso" type="fixed">
    <parent link="base_link"/>
    <child link="torso"/>
    <origin xyz="0 0 0.05"/>
  </joint>

  <!-- Head -->
  <link name="head">
    <visual>
      <geometry>
        <sphere radius="0.1"/>
      </geometry>
      <material name="white">
        <color rgba="1 1 1 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <sphere radius="0.1"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="1.0"/>
      <inertia ixx="0.004" ixy="0" ixz="0" iyy="0.004" iyz="0" izz="0.004"/>
    </inertial>
  </link>

  <!-- Joint connecting torso to head -->
  <joint name="neck_joint" type="revolute">
    <parent link="torso"/>
    <child link="head"/>
    <origin xyz="0 0 0.5"/>
    <axis xyz="0 0 1"/>
    <limit lower="-1.57" upper="1.57" effort="100" velocity="1"/>
  </joint>

  <!-- Left Arm Links -->
  <link name="left_shoulder">
    <visual>
      <geometry>
        <cylinder length="0.15" radius="0.04"/>
      </geometry>
      <origin xyz="0 0 -0.075"/>
      <material name="red">
        <color rgba="1 0 0 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <cylinder length="0.15" radius="0.04"/>
      </geometry>
      <origin xyz="0 0 -0.075"/>
    </collision>
    <inertial>
      <mass value="1.0"/>
      <inertia ixx="0.001" ixy="0" ixz="0" iyy="0.001" iyz="0" izz="0.0005"/>
    </inertial>
  </link>

  <link name="left_upper_arm">
    <visual>
      <geometry>
        <cylinder length="0.3" radius="0.03"/>
      </geometry>
      <origin xyz="0 0 -0.15"/>
      <material name="red"/>
    </visual>
    <collision>
      <geometry>
        <cylinder length="0.3" radius="0.03"/>
      </geometry>
      <origin xyz="0 0 -0.15"/>
    </collision>
    <inertial>
      <mass value="1.5"/>
      <inertia ixx="0.005" ixy="0" ixz="0" iyy="0.005" iyz="0" izz="0.0005"/>
    </inertial>
  </link>

  <link name="left_forearm">
    <visual>
      <geometry>
        <cylinder length="0.25" radius="0.025"/>
      </geometry>
      <origin xyz="0 0 -0.125"/>
      <material name="red"/>
    </visual>
    <collision>
      <geometry>
        <cylinder length="0.25" radius="0.025"/>
      </geometry>
      <origin xyz="0 0 -0.125"/>
    </collision>
    <inertial>
      <mass value="0.8"/>
      <inertia ixx="0.002" ixy="0" ixz="0" iyy="0.002" iyz="0" izz="0.0003"/>
    </inertial>
  </link>

  <!-- Joints for Left Arm -->
  <joint name="left_shoulder_joint" type="revolute">
    <parent link="torso"/>
    <child link="left_shoulder"/>
    <origin xyz="0.1 0 0.35"/>
    <axis xyz="0 1 0"/>
    <limit lower="-1.57" upper="1.57" effort="50" velocity="2"/>
  </joint>

  <joint name="left_elbow_joint" type="revolute">
    <parent link="left_shoulder"/>
    <child link="left_upper_arm"/>
    <origin xyz="0 0 -0.15"/>
    <axis xyz="0 1 0"/>
    <limit lower="0" upper="3.14" effort="40" velocity="2"/>
  </joint>

  <joint name="left_wrist_joint" type="revolute">
    <parent link="left_upper_arm"/>
    <child link="left_forearm"/>
    <origin xyz="0 0 -0.3"/>
    <axis xyz="0 1 0"/>
    <limit lower="-1.57" upper="1.57" effort="30" velocity="3"/>
  </joint>

</robot>
```

## Key Components for Humanoid Robots

### Joint Types for Humanoid Mobility

Humanoid robots require several types of joints to replicate human-like movement:

- **Revolute Joints**: Allow rotation around a single axis (like elbow or knee)
- **Continuous Joints**: Like revolute but unlimited rotation (like shoulders)
- **Prismatic Joints**: Linear sliding motion (less common in humanoids)
- **Fixed Joints**: Rigid connections (like attaching sensors)

### Kinematic Chains

For humanoid robots, key kinematic chains include:
- Right arm chain: torso → shoulder → upper arm → forearm → hand
- Left arm chain: torso → shoulder → upper arm → forearm → hand
- Right leg chain: torso → hip → thigh → shin → foot
- Left leg chain: torso → hip → thigh → shin → foot
- Head chain: torso → neck → head

## Humanoid-Specific Considerations

### Balance and Stability

Humanoid robots must maintain balance, which affects URDF design:
- Center of mass placement
- Foot contact areas for stability
- Distribution of mass across limbs

### Degrees of Freedom (DOF)

A typical humanoid robot might have:
- 6 DOF per arm (shoulder: 3, elbow: 1, wrist: 2)
- 6 DOF per leg (hip: 3, knee: 1, ankle: 2)
- 3 DOF for torso/neck
- Total: approximately 27-30 DOF

### Sensor Integration

URDF files must account for sensors mounted on the humanoid:
- IMU for balance and orientation
- Cameras for vision
- Force/torque sensors in joints
- Touch sensors on hands/feet

## Validation and Testing

Validating your URDF is crucial before simulation or deployment:

```bash
# Check for XML syntax errors
xmllint --noout /path/to/your/robot.urdf

# Check for URDF-specific errors
check_urdf /path/to/your/robot.urdf

# Visualize the robot model
ros2 run rviz2 rviz2
```

## Advanced URDF Features for Humanoids

### Transmission Elements

Define how actuators connect to joints:

```xml
<transmission name="left_shoulder_trans">
  <type>transmission_interface/SimpleTransmission</type>
  <joint name="left_shoulder_joint">
    <hardwareInterface>position_controllers/JointPositionController</hardwareInterface>
  </joint>
  <actuator name="left_shoulder_motor">
    <mechanicalReduction>1</mechanicalReduction>
  </actuator>
</transmission>
```

### Gazebo Integration

Add simulation-specific properties:

```xml
<gazebo reference="left_shoulder">
  <mu1>0.2</mu1>
  <mu2>0.2</mu2>
  <kp>1000000.0</kp>
  <kd>100.0</kd>
</gazebo>
```

## Practical Exercise

Create a URDF file for a simple humanoid robot with:
- A torso and head
- Two arms with 4 DOF each
- Two legs (you can start with basic 3 DOF per leg)
- Proper joint limits and visual representations

Load the URDF in RViz to verify the structure is correct.

## Key Takeaways

- URDF is essential for defining robot kinematics and dynamics
- Humanoid robots require complex kinematic chains to replicate human movement
- Proper inertial properties are critical for simulation accuracy
- Validation tools help catch errors before simulation
- Integration with simulation environments requires special considerations