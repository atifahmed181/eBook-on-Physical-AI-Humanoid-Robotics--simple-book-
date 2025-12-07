#!/usr/bin/env python3

"""
Service Client Example
This script demonstrates how to create a service client node in ROS 2 using rclpy.
It calls the 'add_two_ints' service to add two integers.
"""

import sys
import rclpy
from rclpy.node import Node
from example_interfaces.srv import AddTwoInts


class MinimalClient(Node):
    def __init__(self):
        super().__init__('minimal_client')
        self.cli = self.create_client(AddTwoInts, 'add_two_ints')
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Service not available, waiting again...')
        self.req = AddTwoInts.Request()

    def send_request(self, a, b):
        self.req.a = a
        self.req.b = b
        self.future = self.cli.call_async(self.req)
        rclpy.spin_until_future_complete(self, self.future)
        return self.future.result()


def main(args=None):
    rclpy.init(args=args)
    minimal_client = MinimalClient()
    
    if len(sys.argv) != 3:
        print('Usage: python3 service_client.py <int1> <int2>')
        return
    
    response = minimal_client.send_request(int(sys.argv[1]), int(sys.argv[2]))
    minimal_client.get_logger().info(
        f'Result of add_two_ints: {response.sum}')
    
    minimal_client.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()