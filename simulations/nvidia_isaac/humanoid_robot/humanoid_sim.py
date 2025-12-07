#!/usr/bin/env python3
"""
Isaac Sim Humanoid Robot Environment
This script initializes a basic humanoid robot simulation environment in Isaac Sim.
"""

import omni
from omni.isaac.kit import SimulationApp
from omni.isaac.core import World
from omni.isaac.core.utils.stage import add_reference_to_stage, get_stage_units, set_stage_units
from omni.isaac.core.utils.nucleus import get_assets_root_path
from omni.isaac.core.utils.prims import create_prim
from omni.isaac.core.utils.viewports import set_camera_view
from pxr import Gf
import numpy as np
import carb


# Initialize the simulation application
config = {
    "headless": False,
    "window_width": 1280,
    "window_height": 720,
    "rendering_frequency": 60,
    "clear_color": (0.08, 0.08, 0.08, 1)
}

simulation_app = SimulationApp(config)


def setup_humanoid_environment():
    """
    Set up the humanoid robot simulation environment in Isaac Sim
    """
    # Create world
    world = World(stage_units_in_meters=1.0)

    # Get the assets root path
    assets_root_path = get_assets_root_path()
    if assets_root_path is None:
        carb.log_error("Could not find Isaac Sim assets path")
        return None

    # Add ground plane
    add_reference_to_stage(
        usd_path=f"{assets_root_path}/Isaac/Environments/Simple_Room/simple_room.usd",
        prim_path="/World/ground_plane"
    )

    # Add a simple humanoid robot (using a basic cartpole as placeholder)
    # In a real scenario, you would load a proper humanoid model
    add_reference_to_stage(
        usd_path=f"{assets_root_path}/Isaac/Robots/CartPole/cartpole.usd",
        prim_path="/World/Robot"
    )

    # Add some objects for the robot to navigate
    create_prim(
        prim_path="/World/obstacle1",
        prim_type="Cylinder",
        position=np.array([1.0, 0.5, 0.2]),
        scale=np.array([0.2, 0.2, 0.4]),
        color=np.array([0.8, 0.1, 0.1])
    )

    create_prim(
        prim_path="/World/obstacle2",
        prim_type="Cuboid",
        position=np.array([-1.0, -0.5, 0.3]),
        scale=np.array([0.3, 0.3, 0.6]),
        color=np.array([0.1, 0.1, 0.8])
    )

    # Set up camera view
    set_camera_view(eye=np.array([5, 5, 5]), target=np.array([0, 0, 0]))

    return world


def main():
    """
    Main function to run the humanoid robot simulation
    """
    print("Starting Isaac Sim Humanoid Robot Environment...")

    # Set up the environment
    world = setup_humanoid_environment()
    if world is None:
        simulation_app.close()
        return

    # Reset the world to start simulation
    world.reset()

    # Simulation loop
    print("Simulation running. Press Ctrl+C to exit.")
    try:
        while simulation_app.is_running():
            # Run world step
            world.step(render=True)
    except KeyboardInterrupt:
        print("Simulation interrupted by user")
    finally:
        # Clean up
        simulation_app.close()


if __name__ == "__main__":
    main()