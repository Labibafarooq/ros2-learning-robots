class TerminationChecker:
    """
    Determines when an episode should terminate.
    """

    def __init__(
        self,
        collision_distance=0.25,
        goal_threshold=0.3,
        max_steps=1000,
    ):
        self.collision_distance = collision_distance
        self.goal_threshold = goal_threshold
        self.max_steps = max_steps
        self.step_count = 0

    def reset(self):
        """Reset episode counter."""
        self.step_count = 0

    def check(self, scan_msg, goal_distance):
        """
        Check termination conditions.
        Returns:
            done (bool)
            info (dict)
        """

        self.step_count += 1

        # ----------------------------
        # 1. Goal reached
        # ----------------------------
        if goal_distance < self.goal_threshold:
            return True, {"reason": "goal_reached"}

        # ----------------------------
        # 2. Collision (DISABLED for Stage-1)
        # ----------------------------
        # min_lidar_dist = min(scan_msg.ranges)
        # if min_lidar_dist < self.collision_distance:
        #     return True, {"reason": "collision"}

        # ----------------------------
        # 3. Timeout
        # ----------------------------
        if self.step_count >= self.max_steps:
            return True, {"reason": "timeout"}

        return False, {}
