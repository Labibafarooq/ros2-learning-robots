import numpy as np


class RewardFunction:
    """
    Shape-aware reward function for goal-directed navigation.
    """

    def __init__(
        self,
        collision_distance=0.06,        # 🔧 FIXED
        goal_reward=100.0,
        collision_penalty=-100.0,
        progress_scale=1.0,
        angular_penalty_scale=0.05,
        time_penalty=-0.01,
    ):
        self.collision_distance = collision_distance
        self.goal_reward = goal_reward
        self.collision_penalty = collision_penalty
        self.progress_scale = progress_scale
        self.angular_penalty_scale = angular_penalty_scale
        self.time_penalty = time_penalty

        self.prev_goal_distance = None

    def reset(self):
        """
        Reset episode-specific variables.
        """
        self.prev_goal_distance = None

    def compute(
        self,
        scan_msg,
        odom_msg,
        goal_distance,
        goal_reached=False,
    ):
        """
        Compute the total reward for one timestep.
        """

        reward = 0.0

        # ----------------------------
        # 1. Goal reached (terminal)
        # ----------------------------
        if goal_reached:
            return self.goal_reward

        # ----------------------------
        # 2. Collision penalty
        # ----------------------------
        valid_ranges = [r for r in scan_msg.ranges if r > 0.0]
        min_lidar_dist = min(valid_ranges) if valid_ranges else float('inf')

        if min_lidar_dist < self.collision_distance:
            return self.collision_penalty

        # ----------------------------
        # 3. Progress toward goal
        # ----------------------------
        if self.prev_goal_distance is not None:
            progress = self.prev_goal_distance - goal_distance
            reward += self.progress_scale * progress

        self.prev_goal_distance = goal_distance

        # ----------------------------
        # 4. Smoothness penalty
        # ----------------------------
        angular_vel = abs(odom_msg.twist.twist.angular.z)
        reward -= self.angular_penalty_scale * angular_vel

        # ----------------------------
        # 5. Time penalty
        # ----------------------------
        reward += self.time_penalty

        return float(reward)
