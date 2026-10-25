# Copyright 2026 Robby
# SPDX-License-Identifier: Apache-2.0
"""Run the upstream Nav2 minimal TurtleBot4 in the Depot world."""
import os
import xml.etree.ElementTree as ET

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction, SetEnvironmentVariable
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
import xacro


def robot_state_publisher(context):
    description_share = get_package_share_directory('nav2_minimal_tb4_description')
    path = os.path.join(description_share, 'urdf', 'standard', 'turtlebot4.urdf.xacro')
    robot = ET.fromstring(xacro.process_file(path).toxml())
    # Jetty uses sensor/frame_id; the old camera/optical_frame_id is deprecated.
    for sensor in robot.findall('.//gazebo/sensor'):
        frame = {'rgbd_camera': 'oakd_rgb_camera_optical_frame', 'imu': 'imu_link'}.get(sensor.get('type'))
        if frame:
            element = sensor.find('frame_id')
            if element is None:
                element = ET.SubElement(sensor, 'frame_id')
            element.text = frame
        camera = sensor.find('camera')
        if camera is not None:
            deprecated = camera.find('optical_frame_id')
            if deprecated is not None:
                camera.remove(deprecated)
    description = ET.tostring(robot, encoding='unicode')
    return [Node(
        package='robot_state_publisher', executable='robot_state_publisher',
        name='robot_state_publisher', output='screen',
        parameters=[{'robot_description': ParameterValue(description, value_type=str),
                     'use_sim_time': LaunchConfiguration('use_sim_time')}],
    )]


def generate_launch_description():
    share = get_package_share_directory('turtlebot4_depot')
    sim_share = get_package_share_directory('nav2_minimal_tb4_sim')
    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('headless', default_value='False'),
        DeclareLaunchArgument('nvidia', default_value='false'),
        DeclareLaunchArgument('world', default_value=os.path.join(share, 'worlds', 'depot.sdf')),
        DeclareLaunchArgument('x_pose', default_value='-8.0'),
        DeclareLaunchArgument('y_pose', default_value='0.0'),
        DeclareLaunchArgument('yaw', default_value='0.0'),
        SetEnvironmentVariable('__NV_PRIME_RENDER_OFFLOAD', '1',
                               condition=IfCondition(LaunchConfiguration('nvidia'))),
        SetEnvironmentVariable('__GLX_VENDOR_LIBRARY_NAME', 'nvidia',
                               condition=IfCondition(LaunchConfiguration('nvidia'))),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(sim_share, 'launch', 'simulation.launch.py')),
            launch_arguments={
                'use_sim_time': LaunchConfiguration('use_sim_time'),
                'use_rviz': 'False',
                'use_robot_state_pub': 'False',
                'headless': LaunchConfiguration('headless'),
                'world': LaunchConfiguration('world'),
                'robot_name': 'turtlebot4',
                'x_pose': LaunchConfiguration('x_pose'),
                'y_pose': LaunchConfiguration('y_pose'),
                'yaw': LaunchConfiguration('yaw'),
            }.items(),
        ),
        OpaqueFunction(function=robot_state_publisher),
    ])
