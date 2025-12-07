# Images and Diagrams for the Ebook

This directory contains all images and diagrams used in the "Physical AI and Humanoid Robotics" ebook.

## Directory Structure

```
static/img/
├── module1-ros2/
│   ├── ros2-architecture.png
│   ├── nodes-topics-services-diagram.png
│   ├── rclpy-bridge-architecture.png
│   └── urdf-humanoid-structure.png
├── module2-digital-twin/
│   ├── gazebo-simulation-environment.png
│   ├── unity-humanoid-rendering.png
│   ├── sensor-simulation-diagram.png
│   └── digital-twin-concept.png
├── module3-ai-robot-brain/
│   ├── isaac-sim-overview.png
│   ├── isaac-ros-pipeline.png
│   ├── nav2-architecture.png
│   └── vslam-diagram.png
├── module4-vla/
│   ├── voice-to-action-flow.png
│   ├── cognitive-planning-architecture.png
│   ├── vla-system-overview.png
│   └── capstone-project-diagram.png
└── general/
    ├── humanoid-robot-concept.png
    ├── ebook-cover.png
    └── system-architecture.png
```

## Image Requirements

- Format: PNG, JPG, or SVG for diagrams
- Resolution: High enough for clear viewing (at least 72 DPI)
- Size: Optimized for web delivery
- Naming: Use descriptive, lowercase names with hyphens

## How to Add Images to Markdown

Use the following syntax to include images in markdown files:

```markdown
![Description of image](/img/path-to-image.png)
```

For example:
```markdown
![ROS 2 Architecture](/img/module1-ros2/ros2-architecture.png)
```

## Current Placeholder Images

This is a placeholder directory. In a complete implementation, actual diagrams and images would be created illustrating:

- System architectures
- Code flow diagrams
- Simulation environments
- Robot models and components
- Workflow illustrations
- Technical concept diagrams
```