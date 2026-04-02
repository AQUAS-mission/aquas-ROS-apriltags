import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    # 1. Include the AprilTag launch file
    # This finds the 'aquas_apriltag_bringup' package and runs its 'apriltag.launch.py'
    apriltag_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(
                get_package_share_directory('aquas_apriltag_bringup'),
                'launch', 'apriltag.launch.py'
            )
        ])
    )

    # 2. Define the detections_listener node
    # This is equivalent to 'ros2 run aquas_dock_align detections_listener'
    detections_listener_node = Node(
        package='aquas_dock_align',
        executable='detections_listener',
        name='detections_listener',
        output='screen'
    )

    # Create the launch description and add the actions
    return LaunchDescription([
        apriltag_launch,
        detections_listener_node
    ])
