# Reinforcement Learning–Based Robot Navigation  
### ROS 2 + Gazebo + Proximal Policy Optimization (PPO)

This project implements a complete reinforcement learning (RL) pipeline for autonomous robot navigation using **ROS 2 Jazzy**, **Gazebo**, and **Proximal Policy Optimization (PPO)**.  
A TurtleBot3 robot is trained in simulation to navigate inside a maze environment using LiDAR and odometry data.

---

## Project Overview

The goal of this project is to design and implement an end-to-end reinforcement learning system that allows a mobile robot to:

- Perceive its environment using LiDAR
- Estimate motion using odometry
- Learn collision avoidance
- Navigate safely in a maze-like environment

The entire system is implemented using ROS 2 nodes communicating in real time.

---

## Technologies Used

- ROS 2 Jazzy
- Gazebo Simulation
- Python
- PyTorch
- Proximal Policy Optimization (PPO)
- TurtleBot3

---

## Workspace Structure

```

rosi_rl_ws/
├── src/
│   ├── lr_turtlebot_sim
│   ├── lr_ppo
│   └── lr_ppo_baseline
├── build/
├── install/
├── log/
└── README.md

````

---

## Requirements

- Ubuntu with ROS 2 Jazzy installed
- Gazebo
- Python 3
- PyTorch
- colcon

---

## Building the Workspace

From the workspace root:

```bash
cd ~/rosi_rl_ws
rm -rf build install log
colcon build
````

---

## IMPORTANT (Run in Every Terminal)

Before running **any** ROS 2 command, always source the environment:

```bash
source /opt/ros/jazzy/setup.bash
source ~/rosi_rl_ws/install/setup.bash
```

This step is mandatory and must be done in **every new terminal**.

---

## Running the Project

### 1️⃣ Launch Gazebo Simulation

Open **Terminal 1**, source the environment, then run:

```bash
ros2 launch lr_turtlebot_sim turtlebot_in_maze.launch.py maze:=maze_1
```

This launches:

* Gazebo
* TurtleBot3 robot
* Maze environment
* ROS–Gazebo bridges

---

### 2️⃣ Start the Environment Node

Open **Terminal 2**, source the environment, then run:

```bash
ros2 run lr_ppo env_node
```

The environment node:

* Subscribes to `/scan` and `/odom`
* Builds the observation vector
* Computes the reward function
* Publishes observations and rewards

---

### 3️⃣ Start PPO Training

Open **Terminal 3**, source the environment, then run:

```bash
ros2 run lr_ppo ppo_trainer
```

The PPO trainer:

* Receives observations
* Generates continuous control actions
* Updates the policy during training
* Publishes velocity commands

---

## Observation Space

The observation vector consists of:

* Downsampled LiDAR readings
* Linear velocity (from odometry)
* Angular velocity (from odometry)

This results in a fixed-size observation vector suitable for PPO.

---

## Action Space

The agent outputs continuous actions:

* Linear velocity
* Angular velocity

Actions are applied directly to the robot using `/cmd_vel`.

---

## Reward Function

The reward function includes:

* Positive reward for progress toward the goal
* Penalty for collisions (based on LiDAR distance)
* Penalty for excessive angular velocity
* Small time penalty to encourage efficiency
* Terminal reward for reaching the goal

This reward shaping encourages safe and smooth navigation.

---

## Training Details

* PPO with a neural network policy
* Real-time training in simulation
* Training duration limited due to computational constraints
* Conservative behavior observed during training

Due to limited time and hardware resources, the training was not extended to full convergence.

---

## Evaluation

Evaluation was performed directly in the Gazebo simulation environment.

Observed behavior:

* Slow and cautious movement
* Strong collision avoidance
* Limited exploration
* Robot remained within safe regions of the maze

Although the robot did not consistently reach the goal, the observed behavior confirms that:

* The RL pipeline is functioning correctly
* The agent is learning safety-related behavior
* The PPO implementation is operational

Achieving optimal navigation performance would require significantly longer training time.

---

## Project Status

✔ Full RL pipeline implemented
✔ ROS 2 and Gazebo integrated
✔ PPO algorithm implemented
✔ Observation and reward shaping designed
✔ Real-time training executed
✔ Evaluation performed

---

## Limitations and Future Work

* Increase training time for better convergence
* Improve reward shaping
* Tune action scaling for faster movement
* Save and evaluate trained policies over multiple episodes

---

## Conclusion

This project successfully demonstrates a complete reinforcement learning system for robot navigation using ROS 2 and PPO.
Despite limited training time, the system shows correct learning behavior and provides a solid foundation for further improvements.

---

## Author

Labiba
Master’s Student – Artificial Intelligence
CNAM, France

mubeen
Master's studnet
```

---
