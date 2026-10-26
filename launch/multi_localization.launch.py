# Copyright 2026 Robby
# SPDX-License-Identifier: Apache-2.0
"""Shared-TF localization with one map and distinct robot frame names."""
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def setup(context):
    count = int(LaunchConfiguration('robot_count').perform(context))
    if count not in (2, 3):
        raise ValueError('robot_count must be 2 or 3')
    share = get_package_share_directory('turtlebot4_depot')
    actions = [Node(package='nav2_map_server', executable='map_server', name='map_server',
                    output='screen', parameters=[{'use_sim_time': True, 'frame_id': 'map',
                        'yaml_filename': os.path.join(share, 'maps', 'depot.yaml')}])]
    lifecycle_nodes = ['map_server']
    for i in range(count):
        ns = f'tb4_{i}'
        actions.append(Node(package='nav2_amcl', executable='amcl', name='amcl', namespace=ns,
            output='screen', parameters=[os.path.join(share, 'config', ns+'_amcl.yaml')],
            remappings=[('map', '/map'), ('/tf', '/tf'), ('/tf_static', '/tf_static')]))
        lifecycle_nodes.append(ns+'/amcl')
    actions.append(Node(package='nav2_lifecycle_manager', executable='lifecycle_manager',
        name='lifecycle_manager_localization', output='screen',
        parameters=[{'use_sim_time': True, 'autostart': True,
                     'bond_timeout': 0.0, 'node_names': lifecycle_nodes}]))
    actions.append(Node(package='rviz2', executable='rviz2', name='multi_rviz', output='screen',
        arguments=['-d', os.path.join(share, 'rviz', f'multi_{count}.rviz')],
        parameters=[{'use_sim_time': True}]))
    return actions


def generate_launch_description():
    return LaunchDescription([DeclareLaunchArgument('robot_count', default_value='3'),
                              OpaqueFunction(function=setup)])
