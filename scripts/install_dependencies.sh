#!/usr/bin/env bash
set -euo pipefail

if [[ ${ROS_DISTRO:-} != lyrical ]]; then
    echo '먼저 ROS 2 Lyrical 환경을 불러와주세요.' >&2
    exit 1
fi
sudo apt-get update
sudo apt-get install -y \
    python3-colcon-common-extensions python3-rosdep git \
    ros-lyrical-nav2-minimal-tb4-sim ros-lyrical-navigation2 ros-lyrical-nav2-bringup \
    ros-lyrical-slam-toolbox ros-lyrical-rtabmap-ros \
    ros-lyrical-teleop-twist-keyboard ros-lyrical-tf-transformations
echo '의존성 준비가 끝났습니다. 워크스페이스에서 패키지를 빌드해주세요.'
