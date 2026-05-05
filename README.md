
```markdown
# Greenswip Vision-to-Control Pipeline

A complete ROS 2 perception-to-action pipeline for an Ackerman-steered mobile robot. This project was developed as a technical assignment for Revati Technologies.

The system spawns a custom Ackerman robot in an Ignition Gazebo environment, uses OpenCV to process the onboard camera feed, isolates a specific target box while ignoring decoy shapes, and uses a Proportional (P) controller to navigate the robot to the target without violating non-holonomic Ackerman constraints.

## 🛠️ System Requirements
* **OS:** Ubuntu 22.04 LTS
* **ROS 2:** Humble Hawksbill
* **Simulation:** Ignition Gazebo (Fortress)
* **Dependencies:**
  * `rclpy`
  * `geometry_msgs`
  * `sensor_msgs`
  * `cv_bridge`
  * `ros_gz_bridge`
  * `ros_gz_sim`
  * `robot_state_publisher`
  * `xacro`
  * OpenCV (`python3-opencv`)

## 🏗️ Installation & Setup

1. **Source your ROS 2 installation:**
   ```bash
   source /opt/ros/humble/setup.bash
   
```

2. **Clone this repository into your ROS 2 workspace `src` folder:**
   *(Assuming your workspace is `~/revati_ws`)*
   ```bash
   mkdir -p ~/revati_ws/src
   cd ~/revati_ws/src
   git clone [https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git](https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git)
   ```

3. **Build the workspace:**
   ```bash
   cd ~/revati_ws
   colcon build
   ```

4. **Source the workspace:**
   ```bash
   source install/setup.bash
   
```

## 🚀 Running the Pipeline

To run the complete system, you will need three terminal windows. Remember to run `cd ~/revati_ws` and `source install/setup.bash` in **every** new terminal before running these commands.

**Terminal 1: Launch the Simulation Architecture**
This script parses the Xacro URDF, launches Ignition Gazebo with the `shapes.sdf` world, spawns the robot, and establishes the `ros_gz_bridge` for sensor/velocity data.
```bash
ros2 launch revati_pipeline spawn_robot.launch.py
```
*(Note: If Gazebo launches in a paused state, click the 'Play' button in the bottom left corner to begin sensor publishing).*

**Terminal 2: Start the Perception Node**
This node subscribes to `/camera/image_raw` using a `sensor_data` QoS profile. It applies a custom dual-HSV mask to isolate the dark red target box, calculates the centroid, and publishes the visual offset to the `/visual_error` topic.
```bash
ros2 run revati_pipeline perception_node
```
*(Optional: You can view the live OpenCV tracking feed by running `rviz2` or `rqt_image_view` and subscribing to `/camera/debug_image`).*

**Terminal 3: Start the Control Node**
This node subscribes to `/visual_error` and translates the pixel offset into Ackerman steering commands (`/cmd_vel`). It ensures a constant forward velocity and clamps the steering angle to the physical joint limits.
```bash
ros2 run revati_pipeline control_node
```

## 📂 Project Structure

* **`launch/spawn_robot.launch.py`**: The main launch file combining `robot_state_publisher`, `ros_gz_sim`, and `ros_gz_bridge`.
* **`urdf/ack.urdf.xacro`**: The robot description file, updated with Ignition Gazebo plugins for Ackerman steering and Camera sensor simulation.
* **`worlds/shapes.sdf`**: The simulated environment containing the target Box and decoy shapes (Sphere, Cylinder, Capsule).
* **`revati_pipeline/perception_node.py`**: The OpenCV computer vision node.
* **`revati_pipeline/control_node.py`**: The Ackerman kinematic control node.

