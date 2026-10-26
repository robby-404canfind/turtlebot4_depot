# Copyright 2026 Robby
# SPDX-License-Identifier: Apache-2.0
"""Three Nav2 instances with independent TF topics in one simulator."""
import copy
import os
import tempfile
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (DeclareLaunchArgument, GroupAction, IncludeLaunchDescription,
                            OpaqueFunction, RegisterEventHandler)
from launch.event_handlers import OnShutdown
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
import yaml


def setup(context):
    count = int(LaunchConfiguration('robot_count').perform(context))
    use_rviz = LaunchConfiguration('use_rviz').perform(context).lower() == 'true'
    if count not in (2, 3):
        raise ValueError('robot_count must be 2 or 3')
    share = get_package_share_directory('turtlebot4_depot')
    nav2 = get_package_share_directory('nav2_bringup')
    temporary = tempfile.TemporaryDirectory(prefix='tb4_multi_nav_')
    with open(os.path.join(share, 'config', 'nav2.yaml')) as stream:
        base = yaml.safe_load(stream)
    with open(os.path.join(share, 'rviz', 'navigation.rviz')) as stream:
        rviz_base = yaml.safe_load(stream)
    actions = [
        RegisterEventHandler(OnShutdown(on_shutdown=[OpaqueFunction(
            function=lambda _: temporary.cleanup())])),
        IncludeLaunchDescription(PythonLaunchDescriptionSource(os.path.join(
            share, 'launch', 'multi_simulation.launch.py')),
            launch_arguments={'robot_count': str(count), 'tf_mode': 'isolated',
                              'headless': LaunchConfiguration('headless')}.items()),
    ]
    for i in range(count):
        ns = f'tb4_{i}'
        params = copy.deepcopy(base)
        params['amcl']['ros__parameters']['initial_pose']['y'] = (i-1)*1.5
        params['amcl']['ros__parameters']['saved_pose_filepath'] = os.path.join(
            temporary.name, ns+'_pose')
        params_path = os.path.join(temporary.name, ns+'_nav2.yaml')
        with open(params_path, 'w') as stream:
            yaml.safe_dump(params, stream, sort_keys=False)
        actions.append(GroupAction(actions=[IncludeLaunchDescription(PythonLaunchDescriptionSource(os.path.join(
            nav2, 'launch', 'bringup_launch.py')),
            launch_arguments={'namespace': ns, 'params_file': params_path,
                'map': os.path.join(share, 'maps', 'depot.yaml'),
                'use_sim_time': 'true', 'use_composition': 'true', 'autostart': 'true',
                'use_keepout_zones': 'false', 'use_speed_zones': 'false'}.items())]))
        if use_rviz:
            rviz_config = copy.deepcopy(rviz_base)
            rviz_config['Window Geometry']['X'] = 80 + i*80
            rviz_config['Window Geometry']['Y'] = 70 + i*70
            rviz_path = os.path.join(temporary.name, ns+'_navigation.rviz')
            with open(rviz_path, 'w') as stream:
                yaml.safe_dump(rviz_config, stream, sort_keys=False)
            actions.append(Node(package='rviz2', executable='rviz2', namespace=ns,
                name='rviz2', output='screen', parameters=[{'use_sim_time': True}],
                arguments=['-d', rviz_path],
                remappings=[('/tf', 'tf'), ('/tf_static', 'tf_static')]))
    return actions


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('robot_count', default_value='3'),
        DeclareLaunchArgument('headless', default_value='false'),
        DeclareLaunchArgument('use_rviz', default_value='true'),
        OpaqueFunction(function=setup),
    ])
