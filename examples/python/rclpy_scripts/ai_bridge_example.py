#!/usr/bin/env python3

"""
AI Bridge Example - Obstacle Avoidance
This script demonstrates how to create an AI node that bridges simple decision-making
algorithms to ROS 2 commands using rclpy. It simulates a robot that avoids obstacles
based on distance sensor readings.
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32, String
from geometry_msgs.msg import Twist


class AIBridgeNode(Node):
    def __init__(self):
        super().__init__('ai_bridge_node')
        
        # Publisher for robot movement commands
        self.cmd_vel_publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        
        # Subscriber for sensor data (e.g., distance sensor)
        self.sensor_subscription = self.create_subscription(
            Float32,
            '/distance_sensor',
            self.sensor_callback,
            10
        )
        
        # Publisher for AI decision logs
        self.log_publisher = self.create_publisher(String, '/ai_log', 10)
        
        # Timer to run AI decision-making at regular intervals
        self.timer = self.create_timer(0.1, self.ai_decision_loop)
        
        # Internal state for the AI agent
        self.distance_reading = 0.0
        self.get_logger().info('AI Bridge Node Initialized')

    def sensor_callback(self, msg):
        """Update the internal distance reading when sensor data arrives"""
        self.distance_reading = msg.data
        self.get_logger().debug(f'Distance: {self.distance_reading}')

    def ai_decision_loop(self):
        """Main AI decision-making function"""
        # Simple AI logic: Stop if obstacle too close, otherwise move forward
        cmd_msg = Twist()
        
        if self.distance_reading < 0.5:  # Stop if obstacle within 0.5 meters
            cmd_msg.linear.x = 0.0
            cmd_msg.angular.z = 0.0
            decision = "STOP - Obstacle detected"
        elif self.distance_reading < 1.0:  # Turn if obstacle nearby
            cmd_msg.linear.x = 0.2
            cmd_msg.angular.z = 0.5
            decision = "TURN - Obstacle approaching"
        else:  # Move forward if path is clear
            cmd_msg.linear.x = 0.5
            cmd_msg.angular.z = 0.0
            decision = "FORWARD - Path clear"
        
        # Publish the movement command
        self.cmd_vel_publisher.publish(cmd_msg)
        
        # Log the AI decision
        log_msg = String()
        log_msg.data = f'Decision: {decision}, Distance: {self.distance_reading:.2f}m'
        self.log_publisher.publish(log_msg)
        
        self.get_logger().info(log_msg.data)


def main(args=None):
    rclpy.init(args=args)
    ai_bridge_node = AIBridgeNode()
    
    try:
        rclpy.spin(ai_bridge_node)
    except KeyboardInterrupt:
        pass
    finally:
        ai_bridge_node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()