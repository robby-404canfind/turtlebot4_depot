# Copyright 2026 Robby
# SPDX-License-Identifier: Apache-2.0
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    rtabmap_share = get_package_share_directory('rtabmap_launch')
    share = get_package_share_directory('turtlebot4_depot')
    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('rviz', default_value='true'),
        DeclareLaunchArgument('database_path',
                              default_value=os.path.expanduser('~/.ros/turtlebot4_depot.db')),
        DeclareLaunchArgument('rtabmap_args',
                              default_value='--RGBD/NeighborLinkRefining true --Reg/Strategy 1'),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(rtabmap_share, 'launch', 'rtabmap.launch.py')),
            launch_arguments={
                'use_sim_time': LaunchConfiguration('use_sim_time'),
                'rgb_topic': '/rgbd_camera/image',
                'depth_topic': '/rgbd_camera/depth_image',
                'camera_info_topic': '/rgbd_camera/camera_info',
                'frame_id': 'base_link',
                'odom_topic': '/odom',
                'visual_odometry': 'false',
                'publish_tf_odom': 'false',
                'approx_sync': 'true',
                'qos': '2',
                'database_path': LaunchConfiguration('database_path'),
                'args': LaunchConfiguration('rtabmap_args'),
                'rviz': LaunchConfiguration('rviz'),
                'rviz_cfg': os.path.join(share, 'rviz', 'rgbd.rviz'),
            }.items(),
        ),
    ])
