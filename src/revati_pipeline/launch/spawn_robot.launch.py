import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
import xacro

def generate_launch_description():
    pkg_name = 'revati_pipeline'
    pkg_share = get_package_share_directory(pkg_name)

    # 1. Process the URDF file using Xacro
    urdf_file = os.path.join(pkg_share, 'urdf', 'ack.urdf.xacro')
    robot_description_config = xacro.process_file(urdf_file)
    robot_description = {'robot_description': robot_description_config.toxml()}

    # 2. Start Robot State Publisher (Publishes the physical structure to ROS)
    rsp_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[robot_description, {'use_sim_time': True}]
    )

    # 3. Launch Gazebo (Ignition) and load the shapes.sdf world
    world_file = os.path.join(pkg_share, 'worlds', 'shapes.sdf')
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': f'-r {world_file}'}.items()
    )

    # 4. Spawn the Robot into the Gazebo World
    spawn_node = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', 'ackerman_robot',
            '-topic', 'robot_description',
            '-z', '0.2' # Drops the robot slightly from above the ground
        ],
        output='screen'
    )

    # 5. The Communication Bridge (CRITICAL!)
    # This translates Gazebo data into ROS 2 topics and vice-versa.
    bridge_node = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
          '/cmd_vel@geometry_msgs/msg/Twist]ignition.msgs.Twist',
            '/camera/image_raw@sensor_msgs/msg/Image[ignition.msgs.Image',
            '/clock@rosgraph_msgs/msg/Clock[ignition.msgs.Clock'
        ],
        output='screen'
    )

    return LaunchDescription([
        rsp_node,
        gazebo_launch,
        spawn_node,
        bridge_node
    ])
