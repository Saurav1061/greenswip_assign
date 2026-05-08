```markdown
# 🏎️ Greenswip Vision-to-Control Pipeline
**A ROS 2 Perception & Control System for Ackerman-Steered Robots**

Developed as a technical assignment for **Revati Technologies**, this project demonstrates a full-stack robotics pipeline: spawning a custom Ackerman robot in **Ignition Gazebo**, processing live camera feeds with **OpenCV**, and navigating toward a specific target using a **Proportional (P) Controller**.

---

## 🏗️ System Overview
The pipeline consists of three primary layers working in synchronization:

1.  **Environment & Simulation**: A custom-built URDF robot with Ackerman kinematics spawned in an Ignition Gazebo world containing various geometric primitives.
2.  **Perception (OpenCV)**: A vision node that applies dual-HSV masking to isolate a dark red target while filtering out decoys (spheres, cylinders).
3.  **Control (Ackerman Kinematics)**: A controller that translates visual pixel error into steering angles ($\delta$) and linear velocity ($v$), respecting physical joint limits.

---

## 🛠️ Requirements & Dependencies

| Category | Requirement |
| :--- | :--- |
| **Operating System** | Ubuntu 22.04 LTS |
| **Middleware** | ROS 2 Humble Hawksbill |
| **Simulator** | Ignition Gazebo (Fortress) |
| **Languages** | Python 3.10+, C++ (for core ROS 2) |
| **Libraries** | OpenCV, `cv_bridge`, `xacro` |

---

## 📥 Installation & Setup

1. **Prepare Workspace**
   ```bash
   mkdir -p ~/revati_ws/src
   cd ~/revati_ws/src

```

2. **Clone & Build**
```bash
git clone [https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git](https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git)
cd ~/revati_ws
colcon build --symlink-install


```



```

3. **Environment Configuration**
   Add this to your `~/.bashrc` to save time:
   ```bash
   source /opt/ros/humble/setup.bash
   source ~/revati_ws/install/setup.bash
   

```

---

## 🚀 Execution Guide

To run the pipeline, open three separate terminals. Ensure each is sourced (`source install/setup.bash`).

### Step 1: Launch Simulation

Initializes the Gazebo world, robot state publisher, and the ROS-GZ bridge.

```bash
ros2 launch revati_pipeline spawn_robot.launch.py

```

> **Note:** If Gazebo is paused, press the **Play** button in the GUI to start the physics engine and sensor data stream.

### Step 2: Launch Perception Node

Processes `/camera/image_raw` to find the target.

```bash
ros2 run revati_pipeline perception_node

```

* **Debug Tip:** Use `ros2 run rqt_image_view rqt_image_view` to visualize the `/camera/debug_image` topic.

### Step 3: Launch Control Node

Closes the loop by sending commands to `/cmd_vel`.

```bash
ros2 run revati_pipeline control_node

```

---

## 📂 Repository Structure

```text
revati_pipeline/
├── launch/
│   └── spawn_robot.launch.py   # Orchestrates Gazebo, URDF, and Bridges
├── revati_pipeline/
│   ├── perception_node.py      # OpenCV centroid tracking & HSV filtering
│   └── control_node.py         # P-Controller for Ackerman steering
├── urdf/
│   └── ack.urdf.xacro          # Robot model with Gazebo plugins
├── worlds/
│   └── shapes.sdf              # Simulation environment with target/decoys
├── package.xml                 # Package dependencies
└── setup.py                    # Python entry points and install logic

```

---

## ⚙️ Technical Details

### Perception Strategy

The robot uses a **dual-HSV mask** to ensure robust detection of the red target box across varying light conditions in Gazebo. It filters by area size to ignore small noise and publishes the horizontal pixel offset ($e_x$) from the image center.

### Control Law

The controller utilizes a Proportional (P) gain to determine steering:


$$\delta = K_p \cdot e_x$$


Where:

* $\delta$ is the steering angle.
* $K_p$ is the proportional gain.
* $e_x$ is the normalized visual error.
The node enforces a **saturation limit** on the steering angle to prevent the simulated servo joints from exceeding physical constraints.

```


```
