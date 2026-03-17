import numpy as np


class RewardFunction:
    """
    Shape-aware reward function for goal-directed navigation.
    """

    def __init__(
        self,
        collision_distance=0.06,
    ):
        self.collision_distance = collision_distance
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
        reward = 0.0

        # ----------------------------
        # 1. Goal reached (terminal)
        # ----------------------------
        if goal_reached:
            return 10.0

        # ----------------------------
        # 2. Collision penalty (terminal)
        # ----------------------------
        valid_ranges = [r for r in scan_msg.ranges if r > 0.0]
        min_lidar_dist = min(valid_ranges) if valid_ranges else float('inf')

        if min_lidar_dist < self.collision_distance:
            return -5.0

        # ----------------------------
        # 3. Progress toward goal (CLAMPED)
        # ----------------------------
        if self.prev_goal_distance is not None and goal_distance is not None:
            progress = self.prev_goal_distance - goal_distance
            progress = max(-0.2, min(progress, 0.2))
            reward += progress

        self.prev_goal_distance = goal_distance

        # ----------------------------
        # 4. Smoothness penalty
        # ----------------------------
        angular_vel = abs(odom_msg.twist.twist.angular.z)
        reward -= 0.05 * angular_vel

        # ----------------------------
        # 5. Time penalty
        # ----------------------------
        reward -= 0.01

        return float(reward)
