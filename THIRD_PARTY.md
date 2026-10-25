# Third-party material

- `worlds/depot.sdf` derives from [Nav2 Minimal TurtleBot Simulation](https://github.com/ros-navigation/nav2_minimal_turtlebot_simulation), Apache-2.0. This copy pins the Fuel model to version 6. Copyright Open Source Robotics Foundation, Open Navigation and contributors.
- `config/slam.yaml` derives from [SLAM Toolbox 2.10.0](https://github.com/SteveMacenski/slam_toolbox/blob/2.10.0/config/mapper_params_online_async.yaml), LGPL-2.1. Modified 2026-10-25 for simulation time, `base_link` and TurtleBot4 laser limits. The upstream license is in `LICENSES/LGPL-2.1.txt`.
- Localization launch organization follows Nav2, copyright 2018 Intel Corporation, Apache-2.0.
- TurtleBot4 descriptions and Gazebo bridges are installed from the official Nav2 minimal simulation packages (Apache-2.0); they are not vendored here.
- The [OpenRobotics Depot model](https://app.gazebosim.org/OpenRobotics/fuel/models/Depot), version 6, is downloaded by Gazebo Fuel and is licensed CC BY 4.0. Model geometry and textures are not distributed in this repository. Credit: OpenRobotics.

Original package code is copyright 2026 Robby, Apache-2.0. See `LICENSE`.
