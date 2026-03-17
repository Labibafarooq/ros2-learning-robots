import numpy as np


class ObservationBuilder:
    """
    Builds a fixed-size observation vector for RL.

    Observation:
    - 24 downsampled LiDAR distances
    - Linear velocity
    - Angular velocity
    """

    def __init__(self, num_lidar_beams=24, max_lidar_range=3.5):
        self.num_lidar_beams = num_lidar_beams
        self.max_lidar_range = max_lidar_range

    def process_scan(self, scan_msg):
        """
        Downsample and normalize LiDAR scan.
        """
        ranges = np.array(scan_msg.ranges, dtype=np.float32)

        # Replace inf / nan with max range
        ranges[np.isinf(ranges)] = self.max_lidar_range
        ranges[np.isnan(ranges)] = self.max_lidar_range

        # Downsample
        step = len(ranges) // self.num_lidar_beams
        sampled = ranges[::step][:self.num_lidar_beams]

        # Normalize to [0, 1]
        sampled = np.clip(sampled / self.max_lidar_range, 0.0, 1.0)

        return sampled

    def process_odom(self, odom_msg):
        """
        Extract linear and angular velocity.
        """
        linear_vel = odom_msg.twist.twist.linear.x
        angular_vel = odom_msg.twist.twist.angular.z

        return np.array([linear_vel, angular_vel], dtype=np.float32)

    def build_observation(self, scan_msg, odom_msg):
        """
        Build the full observation vector.
        """
        scan_obs = self.process_scan(scan_msg)
        odom_obs = self.process_odom(odom_msg)

        return np.concatenate([scan_obs, odom_obs])
