# TurtleBot4 Depot

ROS 2 Lyrical / Gazebo Jetty에서 TurtleBot4의 2D SLAM, AMCL, RGB-D SLAM을 실습하기 위한 패키지입니다.

Ubuntu 26.04 / ROS 2 Lyrical / Gazebo Jetty에서 지도 작성·저장, AMCL 위치 추정, RGB-D 3D 지도 생성을 확인했습니다.

로봇 모델과 센서 브리지는 [Nav2 Minimal TurtleBot Simulation](https://github.com/ros-navigation/nav2_minimal_turtlebot_simulation)의 배포 패키지를 사용합니다. 월드는 OpenRobotics의 [Depot](https://app.gazebosim.org/OpenRobotics/fuel/models/Depot)이며 첫 실행 시 Fuel에서 내려받습니다.

## 설치

ROS 2 Lyrical을 설치한 환경에서 실행합니다.

```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src
git clone https://github.com/robby-404canfind/turtlebot4_depot.git
bash ~/ros2_ws/src/turtlebot4_depot/scripts/install_dependencies.sh
cd ~/ros2_ws
rosdep update
rosdep install --from-paths src/turtlebot4_depot --ignore-src -r -y --rosdistro lyrical
colcon build --symlink-install --packages-select turtlebot4_depot
```

워크스페이스 환경을 등록한 새 터미널을 열어 실행합니다. 처음 만든 워크스페이스라면 `source ~/ros2_ws/install/setup.bash`로 환경을 불러옵니다.

```bash
ros2 launch turtlebot4_depot bringup.launch.py
```

하이브리드 NVIDIA 노트북은 `nvidia:=true`를 사용할 수 있습니다.

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -p stamped:=true -p frame_id:=base_link
```

## 2D SLAM

```bash
ros2 launch turtlebot4_depot slam_launch.py
```

지도는 별도 터미널에서 저장합니다.

```bash
cd ~/ros2_ws/src/turtlebot4_depot/maps
ros2 run nav2_map_server map_saver_cli -f depot
cd ~/ros2_ws
colcon build --symlink-install --packages-select turtlebot4_depot
```

## AMCL

SLAM Toolbox를 종료한 후 저장한 지도로 실행합니다.

```bash
ros2 launch turtlebot4_depot localization_launch.py
rviz2 -d ~/ros2_ws/src/turtlebot4_depot/rviz/localization.rviz --ros-args -p use_sim_time:=true
```

## Nav2

SLAM Toolbox 또는 별도 AMCL을 종료한 뒤, 시뮬레이터가 실행 중인 상태에서 시작합니다.

```bash
ros2 launch turtlebot4_depot navigation.launch.py
```

Depot 지도에서 초기 위치는 (0, 0)입니다. Gazebo 월드 좌표의 초기 위치 (-8, 0)와 구분합니다. 기본 DiffDrive MPPI 설정을 사용합니다. BT 반복 주행 9회 도착 및 이동 중 취소 후 귀환, 실제 움직임과 최종 정지를 확인했습니다.

실행 중인 BT/주행 프로그램을 먼저 종료하고, 시뮬레이터가 켜진 상태에서 아래 명령을 실행합니다. 이후 Nav2, 시뮬레이터 순서로 Ctrl+C로 종료합니다.

```bash
ros2 run turtlebot4_depot shutdown_navigation
```

## RGB-D SLAM

SLAM Toolbox와 AMCL을 종료한 뒤 실행합니다.

```bash
ros2 launch turtlebot4_depot rgbd_slam.launch.py
```

RGB-D 카메라와 시뮬레이터의 `/odom`을 사용합니다. 지도 DB는 `~/.ros/turtlebot4_depot.db`에 저장됩니다. 새 지도를 만들 때만 아래 옵션을 지정합니다. 지정한 DB의 이전 지도는 삭제됩니다.

```bash
ros2 launch turtlebot4_depot rgbd_slam.launch.py rtabmap_args:="-d --RGBD/NeighborLinkRefining true --Reg/Strategy 1"
```

## 확인한 버전

- Nav2 minimal TurtleBot4 simulation 1.3.0
- Nav2 1.5.2
- SLAM Toolbox 2.10.0
- RTAB-Map ROS 0.23.13
- Gazebo Sim 10.5.0 (Jetty)

TurtleBot4 센서의 TF 프레임을 Lyrical/Jetty에 맞춰 연결합니다. 센서 주기와 로봇 물리를 별도로 경량화하지 않았습니다.

## 출처

- Nav2 minimal robot/simulation: Apache-2.0, Open Navigation / Open Robotics 및 기여자.
- Depot 월드 구성은 Nav2 minimal simulation의 `depot.sdf`를 사용합니다. 포함된 Depot 모델은 OpenRobotics, CC BY 4.0입니다. 모델은 이 저장소에 복제하지 않습니다.
- Localization 런치 구성은 Apache-2.0의 Nav2 / Intel Corporation 구성에 기반합니다.
