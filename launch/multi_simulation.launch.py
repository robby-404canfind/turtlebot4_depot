# Copyright 2026 Robby
# SPDX-License-Identifier: Apache-2.0
"""Spawn two or three independent TurtleBot4 models in one Depot world."""
import os
import tempfile
import xml.etree.ElementTree as ET

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (AppendEnvironmentVariable, DeclareLaunchArgument,
                            IncludeLaunchDescription, OpaqueFunction,
                            RegisterEventHandler, SetEnvironmentVariable)
from launch.event_handlers import OnShutdown
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
import xacro
import yaml


def setup(context):
    count = int(LaunchConfiguration('robot_count').perform(context))
    mode = LaunchConfiguration('tf_mode').perform(context)
    headless = LaunchConfiguration('headless').perform(context).lower() == 'true'
    if count not in (2, 3) or mode not in ('shared', 'isolated'):
        raise ValueError('robot_count must be 2 or 3; tf_mode must be shared or isolated')
    share = get_package_share_directory('turtlebot4_depot')
    description_share = get_package_share_directory('nav2_minimal_tb4_description')
    sim_share = get_package_share_directory('ros_gz_sim')
    temporary = tempfile.TemporaryDirectory(prefix='tb4_multi_')
    world = os.path.join(temporary.name, 'depot.sdf')
    with open(world, 'w') as stream:
        stream.write(xacro.process_file(os.path.join(share, 'worlds', 'depot.sdf'),
                                       mappings={'headless': str(headless).lower()}).toxml())
    actions = [
        RegisterEventHandler(OnShutdown(on_shutdown=[OpaqueFunction(
            function=lambda _: temporary.cleanup())])),
        IncludeLaunchDescription(PythonLaunchDescriptionSource(
            os.path.join(sim_share, 'launch', 'gz_sim.launch.py')),
            launch_arguments={'gz_args': ['-r -s ', world]}.items()),
        Node(package='ros_gz_bridge', executable='parameter_bridge', name='clock_bridge',
             arguments=['/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'], output='screen'),
    ]
    if not headless:
        actions.append(IncludeLaunchDescription(PythonLaunchDescriptionSource(
            os.path.join(sim_share, 'launch', 'gz_sim.launch.py')),
            launch_arguments={'gz_args': '-g'}.items()))
    for i in range(count):
        ns = f'tb4_{i}'
        prefix = ns + '/' if mode == 'shared' else ''
        robot = ET.fromstring(xacro.process_file(os.path.join(
            description_share, 'urdf', 'standard', 'turtlebot4.urdf.xacro')).toxml())
        names = {e.get('name'): prefix + e.get('name')
                 for e in list(robot.findall('link')) + list(robot.findall('joint'))}
        if prefix:
            for element in robot.iter():
                if element.tag in ('link', 'joint') and element.get('name') in names:
                    element.set('name', names[element.get('name')])
                for attr in ('link', 'reference', 'joint'):
                    if element.get(attr) in names:
                        element.set(attr, names[element.get(attr)])
        for plugin in robot.findall('.//plugin'):
            for element in plugin:
                if element.tag in ('topic', 'odom_topic', 'tf_topic') and element.text:
                    element.text = '/' + ns + '/' + element.text.lstrip('/')
                elif element.tag in ('left_joint', 'right_joint', 'joint_name') and element.text in names:
                    element.text = names[element.text]
                elif element.tag in ('frame_id', 'child_frame_id'):
                    element.text = prefix + element.text
        for sensor in robot.findall('.//gazebo/sensor'):
            topic = sensor.find('topic')
            if topic is not None:
                topic.text = '/' + ns + '/' + topic.text.lstrip('/')
            frame = sensor.find('frame_id')
            if frame is None:
                frame = ET.SubElement(sensor, 'frame_id')
            fixed_frame = {'rgbd_camera': 'oakd_rgb_camera_optical_frame', 'imu': 'imu_link'}.get(sensor.get('type'))
            frame.text = prefix + (fixed_frame or frame.text)
            camera = sensor.find('camera')
            if camera is not None and camera.find('optical_frame_id') is not None:
                camera.remove(camera.find('optical_frame_id'))
        description = ET.tostring(robot, encoding='unicode')
        tf = '/tf' if mode == 'shared' else f'/{ns}/tf'
        tf_static = '/tf_static' if mode == 'shared' else f'/{ns}/tf_static'
        actions.extend([
            Node(package='robot_state_publisher', executable='robot_state_publisher',
                 namespace=ns, name='robot_state_publisher', output='screen',
                 parameters=[{'use_sim_time': True, 'robot_description': ParameterValue(description, value_type=str)}],
                 remappings=[('/tf', tf), ('/tf_static', tf_static)]),
            Node(package='ros_gz_sim', executable='create', namespace=ns, output='screen',
                 arguments=['-name', ns, '-topic', f'/{ns}/robot_description',
                            '-x', '-8.0', '-y', str((i-1)*1.5), '-z', '0.01']),
        ])
        bridges = []
        for topic_name, ros_type, gz_type, direction in [
            ('joint_states', 'sensor_msgs/msg/JointState', 'gz.msgs.Model', 'GZ_TO_ROS'),
            ('odom', 'nav_msgs/msg/Odometry', 'gz.msgs.Odometry', 'GZ_TO_ROS'),
            ('tf', 'tf2_msgs/msg/TFMessage', 'gz.msgs.Pose_V', 'GZ_TO_ROS'),
            ('scan', 'sensor_msgs/msg/LaserScan', 'gz.msgs.LaserScan', 'GZ_TO_ROS'),
            ('imu', 'sensor_msgs/msg/Imu', 'gz.msgs.IMU', 'GZ_TO_ROS'),
            ('cmd_vel', 'geometry_msgs/msg/TwistStamped', 'gz.msgs.Twist', 'ROS_TO_GZ'),
            ('rgbd_camera/camera_info', 'sensor_msgs/msg/CameraInfo', 'gz.msgs.CameraInfo', 'GZ_TO_ROS'),
        ]:
            bridges.append(dict(ros_topic_name=tf if topic_name == 'tf' else f'/{ns}/{topic_name}',
                                gz_topic_name=f'/{ns}/{topic_name}', ros_type_name=ros_type,
                                gz_type_name=gz_type, direction=direction))
        bridge_file = os.path.join(temporary.name, ns + '_bridge.yaml')
        with open(bridge_file, 'w') as stream:
            yaml.safe_dump(bridges, stream)
        actions.append(Node(package='ros_gz_bridge', executable='parameter_bridge', namespace=ns,
                            name='bridge_ros_gz', output='screen',
                            parameters=[{'config_file': bridge_file, 'use_sim_time': True}]))
        actions.append(Node(package='ros_gz_image', executable='image_bridge', namespace=ns,
                            name='camera_bridge', output='screen', parameters=[{'use_sim_time': True}],
                            arguments=[f'/{ns}/rgbd_camera/image', f'/{ns}/rgbd_camera/depth_image']))
    return actions


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('robot_count', default_value='3'),
        DeclareLaunchArgument('tf_mode', default_value='shared'),
        DeclareLaunchArgument('headless', default_value='false'),
        AppendEnvironmentVariable('GZ_SIM_RESOURCE_PATH', os.path.join(
            get_package_share_directory('nav2_minimal_tb4_sim'), 'worlds')),
        OpaqueFunction(function=setup),
    ])
