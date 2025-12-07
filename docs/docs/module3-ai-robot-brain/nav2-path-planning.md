---
sidebar_position: 4
---

# Nav2: Path Planning for Bipedal Humanoid Movement

## Introduction to Navigation for Humanoid Robots

Navigation for humanoid robots presents unique challenges compared to wheeled or tracked robots. Bipedal locomotion requires careful consideration of balance, step placement, and dynamic stability. Nav2, the navigation stack for ROS 2, provides the framework for path planning, but requires specific adaptations for humanoid robots.

## Challenges in Humanoid Navigation

### Balance and Stability
Unlike wheeled robots, humanoid robots must maintain balance during navigation. Each step must be carefully planned to maintain the center of mass within the support polygon created by the feet.

### Step Sequence Planning
Humanoid robots navigate by taking discrete steps rather than continuous motion, requiring path planners to consider:
- Footstep placement
- Balance between steps
- Dynamic stability margins
- Terrain traversability

### Dynamic Constraints
Humanoid robots have complex dynamic constraints:
- Limited turning in place
- Forward momentum preference
- Balance recovery capabilities
- Variable step length and timing

## Nav2 Architecture for Humanoid Robots

### Custom Costmaps
Humanoid robots require specialized costmaps that consider factors beyond simple obstacles:

```yaml
# Costmap parameters for humanoid navigation
local_costmap:
  local_costmap:
    ros__parameters:
      update_frequency: 10.0
      publish_frequency: 5.0
      global_frame: odom
      robot_base_frame: base_link
      use_sim_time: true
      rolling_window: true
      width: 20
      height: 20
      resolution: 0.1
      robot_radius: 0.4  # Larger than typical to account for walking pattern
      
      plugins: ["static_layer", "obstacle_layer", "inflation_layer", "slope_layer"]
      
      obstacle_layer:
        plugin: "nav2_costmap_2d::ObstacleLayer"
        enabled: True
        observation_sources: laser_scan
        laser_scan:
          topic: /scan
          max_obstacle_height: 2.0
          clearing: True
          marking: True
          
      # Custom layer for slope analysis
      slope_layer:
        plugin: "nav2_costmap_2d::SlopeLayer"
        enabled: True
        max_slope: 0.3  # Maximum traversable slope (30 degrees)
        slope_threshold: 0.2  # Start marking as difficult at 20 degrees
          
      inflation_layer:
        plugin: "nav2_costmap_2d::InflationLayer"
        cost_scaling_factor: 2.0  # Adjust for humanoid safety margin
        inflation_radius: 0.8     # Larger safety margin for bipedal stability
```

### Custom Planners
For humanoid robots, we often need custom planners that consider bipedal constraints:

```python
# Example: Custom footstep planner for humanoid navigation
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import ComputePathToPose
from rclpy.action import ActionServer
import numpy as np

class HumanoidPathPlanner(Node):
    def __init__(self):
        super().__init__('humanoid_path_planner')
        
        # Create action server for path computation
        self._action_server = ActionServer(
            self,
            ComputePathToPose,
            'compute_path_to_pose',
            self.execute_path_planning
        )
        
    def execute_path_planning(self, goal_handle):
        self.get_logger().info('Received path planning request')
        
        # Get start and goal poses
        start_pose = self.get_current_pose()
        goal_pose = goal_handle.request.goal
        
        # Plan path considering humanoid constraints
        path = self.plan_humanoid_path(start_pose, goal_pose)
        
        # Create result
        result = ComputePathToPose.Result()
        result.path = path
        
        goal_handle.succeed()
        return result
        
    def plan_humanoid_path(self, start, goal):
        # Simplified implementation - in practice, this would be complex
        # Calculate waypoints that consider step constraints
        
        # Generate intermediate waypoints
        waypoints = self.generate_waypoints(start, goal)
        
        # Validate each waypoint for humanoid traversability
        valid_path = self.validate_path_for_humanoid(waypoints)
        
        return valid_path
        
    def generate_waypoints(self, start, goal):
        # Generate waypoints considering maximum step length
        max_step_length = 0.6  # meters
        
        # Calculate straight-line path
        dx = goal.pose.position.x - start.pose.position.x
        dy = goal.pose.position.y - start.pose.position.y
        distance = np.sqrt(dx**2 + dy**2)
        
        # Divide into steps that humanoid can take
        num_steps = int(np.ceil(distance / max_step_length))
        
        waypoints = []
        for i in range(num_steps + 1):
            t = i / num_steps if num_steps > 0 else 0
            waypoint = PoseStamped()
            waypoint.pose.position.x = start.pose.position.x + t * dx
            waypoint.pose.position.y = start.pose.position.y + t * dy
            waypoint.pose.position.z = start.pose.position.z
            waypoints.append(waypoint)
            
        return waypoints
        
    def validate_path_for_humanoid(self, waypoints):
        # Check each waypoint for traversability
        # Consider slope, obstacles, step size constraints
        valid_waypoints = []
        
        for waypoint in waypoints:
            if self.is_waypoint_traversable(waypoint):
                valid_waypoints.append(waypoint)
            else:
                # Find alternative route or abort
                self.get_logger().warn(f'Waypoint not traversable: {waypoint}')
                
        return valid_waypoints
        
    def is_waypoint_traversable(self, waypoint):
        # Check if waypoint is safe for humanoid to step on
        # Consider slope, obstacle height, surface type
        return True  # Simplified implementation

def main(args=None):
    rclpy.init(args=args)
    planner = HumanoidPathPlanner()
    
    try:
        rclpy.spin(planner)
    except KeyboardInterrupt:
        pass
    finally:
        planner.destroy_node()
        rclpy.shutdown()
```

## Bipedal-Specific Navigation Controllers

### Footstep Planning
```python
# Footstep planning for humanoid navigation
import numpy as np
from scipy.spatial.transform import Rotation as R

class FootstepPlanner:
    def __init__(self):
        self.step_width = 0.25  # Distance between feet
        self.max_step_length = 0.6  # Max forward step
        self.max_step_height = 0.1  # Max step-up height
        
    def plan_footsteps(self, path, current_left_foot, current_right_foot):
        """Plan a sequence of footsteps from a path"""
        footsteps = []
        
        # Start with current foot positions
        left_foot = current_left_foot.copy()
        right_foot = current_right_foot.copy()
        
        # Alternate feet for stability
        use_left_first = self.distance_to_goal(left_foot, path[0]) < self.distance_to_goal(right_foot, path[0])
        
        for i, target_pose in enumerate(path):
            if i == 0:  # Skip first (current position)
                continue
                
            # Determine which foot to move
            if (i % 2 == 0 and use_left_first) or (i % 2 == 1 and not use_left_first):
                # Move left foot
                target_pos = self.calculate_foot_placement(left_foot, target_pose, 'left')
                footsteps.append(('left', target_pos))
                left_foot = target_pos.copy()
            else:
                # Move right foot
                target_pos = self.calculate_foot_placement(right_foot, target_pose, 'right')
                footsteps.append(('right', target_pos))
                right_foot = target_pos.copy()
                
        return footsteps
        
    def calculate_foot_placement(self, current_foot, target_pose, foot_type):
        """Calculate optimal placement for next footstep"""
        # Simplified implementation
        # In practice, this would consider balance, terrain, and dynamics
        target_pos = np.array([target_pose.pose.position.x, 
                              target_pose.pose.position.y, 
                              target_pose.pose.position.z])
        
        # Add small offset based on foot type for stability
        if foot_type == 'left':
            target_pos[1] += self.step_width / 2
        else:  # right
            target_pos[1] -= self.step_width / 2
            
        return target_pos
```

### Balance-Aware Controllers
```python
# Balance-aware navigation controller
class BalanceAwareController:
    def __init__(self):
        self.zmp_reference = np.array([0.0, 0.0])  # Zero Moment Point reference
        self.com_height = 0.8  # Center of mass height
        self.stability_margin = 0.1  # Safety margin for balance
        
    def calculate_stable_trajectory(self, path, robot_state):
        """Calculate a trajectory that maintains balance"""
        # Ensure ZMP (Zero Moment Point) stays within support polygon
        trajectory = []
        
        for waypoint in path:
            # Check if waypoint maintains balance
            if self.is_stable_at_waypoint(waypoint, robot_state):
                trajectory.append(waypoint)
            else:
                # Adjust waypoint to maintain stability
                adjusted_waypoint = self.adjust_for_stability(waypoint, robot_state)
                trajectory.append(adjusted_waypoint)
                
        return trajectory
        
    def is_stable_at_waypoint(self, waypoint, robot_state):
        """Check if robot can maintain balance at waypoint"""
        # Calculate ZMP and check if it's within support polygon
        zmp = self.calculate_zmp(waypoint, robot_state)
        support_polygon = self.calculate_support_polygon(robot_state)
        
        return self.point_in_polygon(zmp, support_polygon)
        
    def calculate_zmp(self, waypoint, robot_state):
        """Calculate Zero Moment Point"""
        # Simplified ZMP calculation
        # In practice, this would use full dynamics model
        return np.array([waypoint.pose.position.x, waypoint.pose.position.y])
        
    def point_in_polygon(self, point, polygon):
        """Check if point is inside polygon using ray casting"""
        x, y = point
        n = len(polygon)
        inside = False
        
        p1x, p1y = polygon[0]
        for i in range(1, n + 1):
            p2x, p2y = polygon[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
            
        return inside
```

## Integration with Isaac ROS

### Hardware-Accelerated Path Planning
```python
# Using Isaac ROS for perception-enhanced navigation
class IsaacROSNavPlanner:
    def __init__(self):
        # Initialize Isaac ROS perception nodes
        self.setup_isaac_perception()
        
    def setup_isaac_perception(self):
        # Setup Isaac ROS visual SLAM and perception
        # This provides enhanced environment awareness
        pass
        
    def plan_path_with_perception(self, goal):
        # Use Isaac ROS perception data to enhance path planning
        # Detect and plan around dynamic obstacles
        # Use semantic information to identify traversable terrain
        
        # Get enhanced map from Isaac ROS perception
        enhanced_map = self.get_enhanced_map()
        
        # Plan path using enhanced environmental understanding
        path = self.plan_path_with_enhanced_map(goal, enhanced_map)
        
        return path
```

## Practical Exercise

Implement a complete humanoid navigation system with:
1. A custom costmap layer that considers slope and terrain traversability
2. A footstep planner that generates safe stepping sequences
3. A balance-aware controller that maintains stability during navigation
4. Integration with Isaac ROS perception for enhanced obstacle detection
5. A complete navigation pipeline from global path planning to local footstep execution

## Key Takeaways

- Humanoid navigation requires specialized path planning that considers bipedal dynamics
- Footstep planning is crucial for maintaining balance during locomotion
- Balance-aware controllers ensure stability during navigation
- Integration with perception systems enables safe navigation in complex environments
- Custom costmaps that consider terrain properties are essential for humanoid robots