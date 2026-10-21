from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():

    pkg_share = get_package_share_directory('aquas_apriltag_bringup')
    
    

    apriltag_params = {"family": "36h11",
    "size": 0.165 }
    camera_params = { "camera_info_url": "file:///home/xavier/Developer/aquas-ROS-apriltags/src/aquas_apriltag_bringup/config/my_camera_calibration.yaml",
    "camera_name": "my_camera",
    "device": "/dev/video0"}

    camera_node = Node(
        package='v4l2_camera',
        executable='v4l2_camera_node',
        parameters=[camera_params],
        output='screen'
    )

    apriltag_node = Node(
        package='apriltag_ros',
        executable='apriltag_node',
        parameters=[apriltag_params],
        remappings=[
            ('/image_rect', '/image_raw'),
            ('/camera_info', '/camera_info')
        ],
        output='screen'
    )

    return LaunchDescription([
        camera_node,
        apriltag_node
    ])
