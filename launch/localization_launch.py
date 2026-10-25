# Copyright (c) 2018 Intel Corporation
# Copyright 2026 Robby
# SPDX-License-Identifier: Apache-2.0
"""Map server and AMCL with an explicit lifecycle manager for the service exercises."""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from nav2_common.launch import RewrittenYaml


def generate_launch_description():
    my_nav_dir = get_package_share_directory('turtlebot4_depot')
    my_param_dir = os.path.join(my_nav_dir, 'config')
    my_param_file = 'amcl.yaml'
    my_map_dir = os.path.join(my_nav_dir, 'maps')
    my_map_file = 'depot.yaml'

    use_sim_time = LaunchConfiguration('use_sim_time')
    autostart = LaunchConfiguration('autostart')
    map_yaml_file = LaunchConfiguration('map')
    params_file = LaunchConfiguration('params_file')
    lifecycle_nodes = ['map_server', 'amcl']

    param_substitutions = {
        'use_sim_time': use_sim_time,
        'yaml_filename': map_yaml_file,
    }
    configured_params = RewrittenYaml(
        source_file=params_file,
        root_key='',
        param_rewrites=param_substitutions,
        convert_types=True,
    )
    return LaunchDescription([
        DeclareLaunchArgument('map', default_value=os.path.join(my_map_dir, my_map_file)),
        DeclareLaunchArgument('params_file',
                              default_value=os.path.join(my_param_dir, my_param_file)),
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('autostart', default_value='true'),
        Node(
            package='nav2_map_server', executable='map_server', name='map_server',
            output='screen', parameters=[configured_params],
        ),
        Node(
            package='nav2_amcl', executable='amcl', name='amcl',
            output='screen', parameters=[configured_params],
        ),
        Node(
            package='nav2_lifecycle_manager', executable='lifecycle_manager',
            name='lifecycle_manager_localization', output='screen',
            parameters=[{'use_sim_time': use_sim_time},
                        {'autostart': autostart},
                        {'node_names': lifecycle_nodes}],
        ),
    ])
