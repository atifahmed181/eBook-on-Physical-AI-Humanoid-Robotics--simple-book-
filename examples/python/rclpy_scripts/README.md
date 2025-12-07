# rclpy Examples

This directory contains example Python scripts demonstrating the use of rclpy, the Python client library for ROS 2.

## Available Examples

### Basic Communication
- `simple_publisher.py` - Demonstrates how to create a publisher node that sends messages to a topic
- `simple_subscriber.py` - Shows how to create a subscriber node that receives messages from a topic
- `service_server.py` - Implements a service server that responds to requests
- `service_client.py` - Implements a service client that sends requests to a server

### AI Integration
- `ai_bridge_example.py` - Shows how to connect AI decision-making algorithms to ROS 2 commands

## Running the Examples

To run any of these examples, make sure ROS 2 is sourced in your environment:

```bash
# On Linux
source /opt/ros/<ros2-distro>/setup.bash

# On Windows, source the ROS 2 environment
```

Then run the Python script:

```bash
python3 simple_publisher.py
```

For the service client example, you need to run it with two integer arguments:

```bash
python3 service_client.py 10 20
```

## Requirements

- ROS 2 (with rclpy)
- Python 3.6+
- Standard ROS 2 message packages (std_msgs, geometry_msgs, example_interfaces)