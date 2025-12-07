---
sidebar_position: 3
---

# Cognitive Planning: Using LLMs to Translate Natural Language into ROS 2 Actions

## Introduction to Cognitive Planning

Cognitive planning bridges the gap between high-level natural language instructions and low-level robot actions. By leveraging Large Language Models (LLMs), humanoid robots can interpret complex, ambiguous, or multi-step commands and generate appropriate sequences of ROS 2 actions to accomplish the requested tasks.

## Understanding Cognitive Planning in Robotics

### The Planning Pipeline

Cognitive planning in robotics typically involves several stages:

1. **Natural Language Understanding**: Interpreting the user's intent from spoken or written commands
2. **Task Decomposition**: Breaking down complex tasks into simpler, executable subtasks
3. **Action Sequencing**: Arranging subtasks into a sequence of robot actions
4. **Execution Monitoring**: Ensuring successful completion and adapting to changes

### Integration with ROS 2

LLMs can be integrated into ROS 2 systems through several approaches:
- Action servers that call LLM APIs
- Behavior trees with LLM-based decision nodes
- Natural language interfaces that generate ROS messages

## Implementing Cognitive Planning with LLMs

### Basic LLM Integration Node
```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from action_msgs.msg import GoalStatus
from geometry_msgs.msg import Pose, Point
import json
import openai  # or any other LLM API
import time

class CognitivePlanningNode(Node):
    def __init__(self):
        super().__init__('cognitive_planning_node')
        
        # Subscriber for natural language commands
        self.command_sub = self.create_subscription(
            String,
            'natural_language_command',
            self.command_callback,
            10
        )
        
        # Publishers for ROS 2 actions
        self.move_goal_pub = self.create_publisher(String, 'move_base/goal', 10)
        self.manipulation_goal_pub = self.create_publisher(String, 'manipulation/goal', 10)
        self.action_sequence_pub = self.create_publisher(String, 'action_sequence', 10)
        
        # Initialize LLM client (replace with your preferred LLM)
        # openai.api_key = 'your-api-key-here'
        
        self.get_logger().info('Cognitive Planning Node initialized')

    def command_callback(self, msg):
        """Process incoming natural language command"""
        command = msg.data
        self.get_logger().info(f'Received command: {command}')
        
        # Generate action plan using LLM
        action_plan = self.generate_action_plan(command)
        
        if action_plan:
            self.execute_action_plan(action_plan)
        else:
            self.get_logger().warn(f'Could not generate action plan for: {command}')

    def generate_action_plan(self, command):
        """Generate an action plan from natural language using LLM"""
        # Define the system prompt for the LLM
        system_prompt = """
        You are an assistant that converts natural language commands into robot action sequences.
        Please analyze the user's command and break it down into specific robot actions.
        
        Each action should be in the following format:
        {
            "action": "action_type",
            "parameters": {"param1": "value1", "param2": "value2"},
            "description": "Human-readable description"
        }
        
        Available action types:
        - NAVIGATE_TO: Navigate to a specific location
        - IDENTIFY_OBJECT: Look for a specific object in the environment
        - GRASP_OBJECT: Pick up an identified object
        - PLACE_OBJECT: Put down an object at a location
        - PERFORM_ACTION: Execute a specific action (wave, nod, etc.)
        
        Return only the JSON action sequence, no additional text.
        """
        
        try:
            # Example using OpenAI API (replace with your LLM of choice)
            # response = openai.ChatCompletion.create(
            #     model="gpt-3.5-turbo",
            #     messages=[
            #         {"role": "system", "content": system_prompt},
            #         {"role": "user", "content": f"Command: {command}"}
            #     ],
            #     temperature=0.1
            # )
            # 
            # # Parse the response
            # content = response.choices[0].message.content
            
            # For demonstration, we'll use a mock implementation:
            action_plan = self.mock_generate_action_plan(command)
            
            # Log the generated plan
            self.get_logger().info(f'Generated action plan: {json.dumps(action_plan, indent=2)}')
            
            return action_plan
            
        except Exception as e:
            self.get_logger().error(f'Error generating action plan: {e}')
            return None

    def mock_generate_action_plan(self, command):
        """Mock implementation of LLM-based action planning"""
        # This is a simplified mock implementation
        # In a real system, this would be replaced with actual LLM calls
        
        command_lower = command.lower()
        
        if 'clean the room' in command_lower:
            return [
                {
                    "action": "NAVIGATE_TO",
                    "parameters": {"location": "desk_area"},
                    "description": "Navigate to desk area to start cleaning"
                },
                {
                    "action": "IDENTIFY_OBJECT",
                    "parameters": {"object_type": "clutter"},
                    "description": "Look for cluttered items"
                },
                {
                    "action": "GRASP_OBJECT",
                    "parameters": {"object_id": "item1"},
                    "description": "Pick up the first cluttered item"
                },
                {
                    "action": "NAVIGATE_TO",
                    "parameters": {"location": "storage_bin"},
                    "description": "Navigate to storage area"
                },
                {
                    "action": "PLACE_OBJECT",
                    "parameters": {"location": "storage_bin"},
                    "description": "Place item in storage"
                }
            ]
        elif 'pick up the red ball' in command_lower:
            return [
                {
                    "action": "IDENTIFY_OBJECT",
                    "parameters": {"object_type": "ball", "color": "red"},
                    "description": "Look for the red ball"
                },
                {
                    "action": "NAVIGATE_TO",
                    "parameters": {"relative_position": "near_object"},
                    "description": "Move closer to the ball"
                },
                {
                    "action": "GRASP_OBJECT",
                    "parameters": {"object_id": "red_ball"},
                    "description": "Pick up the red ball"
                }
            ]
        elif 'bring me coffee' in command_lower:
            return [
                {
                    "action": "NAVIGATE_TO",
                    "parameters": {"location": "kitchen"},
                    "description": "Go to kitchen to get coffee"
                },
                {
                    "action": "IDENTIFY_OBJECT",
                    "parameters": {"object_type": "coffee_cup"},
                    "description": "Look for coffee cup"
                },
                {
                    "action": "GRASP_OBJECT",
                    "parameters": {"object_id": "coffee_cup"},
                    "description": "Pick up the coffee cup"
                },
                {
                    "action": "NAVIGATE_TO",
                    "parameters": {"location": "user_position"},
                    "description": "Return to the user"
                },
                {
                    "action": "PLACE_OBJECT",
                    "parameters": {"location": "near_user"},
                    "description": "Give coffee to user"
                }
            ]
        else:
            # Default response for unrecognized commands
            return [
                {
                    "action": "PERFORM_ACTION",
                    "parameters": {"action_type": "acknowledge"},
                    "description": "Acknowledge the command"
                }
            ]

    def execute_action_plan(self, action_plan):
        """Execute the generated action plan"""
        for i, action in enumerate(action_plan):
            self.get_logger().info(f'Executing action {i+1}/{len(action_plan)}: {action["description"]}')
            
            if action["action"] == "NAVIGATE_TO":
                self.execute_navigation(action["parameters"])
            elif action["action"] == "IDENTIFY_OBJECT":
                self.execute_object_identification(action["parameters"])
            elif action["action"] == "GRASP_OBJECT":
                self.execute_grasping(action["parameters"])
            elif action["action"] == "PLACE_OBJECT":
                self.execute_placing(action["parameters"])
            elif action["action"] == "PERFORM_ACTION":
                self.execute_general_action(action["parameters"])
            
            # Add a small delay between actions
            time.sleep(0.5)
    
    def execute_navigation(self, params):
        """Execute navigation action"""
        # Publish navigation goal to MoveBase action server
        goal_msg = String()
        goal_msg.data = json.dumps(params)
        self.move_goal_pub.publish(goal_msg)
        self.get_logger().info(f'Navigating to: {params}')

    def execute_object_identification(self, params):
        """Execute object identification action"""
        # Trigger object detection pipeline
        self.get_logger().info(f'Looking for object: {params}')

    def execute_grasping(self, params):
        """Execute grasping action"""
        # Publish to manipulation stack
        manip_msg = String()
        manip_msg.data = json.dumps(params)
        self.manipulation_goal_pub.publish(manip_msg)
        self.get_logger().info(f'Grasping object: {params}')

    def execute_placing(self, params):
        """Execute placing action"""
        # Publish to manipulation stack for placing
        manip_msg = String()
        manip_msg.data = json.dumps(params)
        self.manipulation_goal_pub.publish(manip_msg)
        self.get_logger().info(f'Placing object: {params}')

    def execute_general_action(self, params):
        """Execute general robot action"""
        self.get_logger().info(f'Performing action: {params}')

def main(args=None):
    rclpy.init(args=args)
    node = CognitivePlanningNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()