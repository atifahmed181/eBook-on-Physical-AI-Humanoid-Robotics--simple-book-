import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.
 */
const sidebars: SidebarsConfig = {
  // Manual sidebar configuration for the ebook
  tutorialSidebar: [
    'intro',
    {
      type: 'category',
      label: 'Module 1: Robotic Nervous System (ROS 2)',
      items: [
        'module1-ros2/index',
        'module1-ros2/nodes-topics-services',
        'module1-ros2/rclpy-bridge',
        'module1-ros2/urdf-for-humanoids',
      ],
      collapsed: false,
    },
    {
      type: 'category',
      label: 'Module 2: Digital Twin (Gazebo & Unity)',
      items: [
        'module2-digital-twin/index',
        'module2-digital-twin/gazebo-physics',
        'module2-digital-twin/unity-rendering',
        'module2-digital-twin/simulating-sensors',
      ],
      collapsed: false,
    },
    {
      type: 'category',
      label: 'Module 3: AI-Robot Brain (NVIDIA Isaac™)',
      items: [
        'module3-ai-robot-brain/index',
        'module3-ai-robot-brain/nvidia-isaac-sim',
        'module3-ai-robot-brain/isaac-ros',
        'module3-ai-robot-brain/nav2-path-planning',
      ],
      collapsed: false,
    },
    {
      type: 'category',
      label: 'Module 4: Vision-Language-Action (VLA)',
      items: [
        'module4-vla/index',
        'module4-vla/voice-to-action',
        'module4-vla/cognitive-planning',
        'module4-vla/capstone-project',
      ],
      collapsed: false,
    },
  ],
};

export default sidebars;