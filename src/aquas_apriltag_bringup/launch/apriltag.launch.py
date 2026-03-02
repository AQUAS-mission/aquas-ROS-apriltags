from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():

    pkg_share = get_package_share_directory('aquas_apriltag_bringup')

    apriltag_params = os.path.join(pkg_share, 'config', 'apriltag.yaml')
    camera_params = os.path.join(pkg_share, 'config', 'camera.yaml')

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
