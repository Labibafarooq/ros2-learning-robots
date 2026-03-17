import rclpy
from rclpy.node import Node

from geometry_msgs.msg import TwistStamped
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry
from std_msgs.msg import Float32MultiArray

from lr_ppo_baseline.observation import ObservationBuilder
from lr_ppo_baseline.reward import RewardFunction
from lr_ppo_baseline.termination import TerminationChecker


class EnvNode(Node):
    def __init__(self):
        super().__init__('env_node')

        # --------------------
        # Publishers
        # --------------------
        self.cmd_pub = self.create_publisher(
        TwistStamped, '/cmd_vel', 10
        )
        self.obs_pub = self.create_publisher(
            Float32MultiArray, '/ppo/observation', 10
        )

        # --------------------
        # PPO action subscriber
        # --------------------
#        self.latest_action = None
 #       self.action_sub = self.create_subscription(
  #          Float32MultiArray,
   #         '/ppo/action',
    #        self.action_callback,
     #       10
      #  )

        # --------------------
        # Sensors
        # --------------------
        self.scan_sub = self.create_subscription(
            LaserScan, '/scan', self.scan_callback, 10
        )
        self.odom_sub = self.create_subscription(
            Odometry, '/odom', self.odom_callback, 10
        )

        # --------------------
        # Timer (10 Hz)
        # --------------------
        self.timer = self.create_timer(0.1, self.step)

        # --------------------
        # RL components
        # --------------------
        self.obs_builder = ObservationBuilder()
        self.reward_fn = RewardFunction()
        self.termination_checker = TerminationChecker()

        # --------------------
        # State
        # --------------------
        self.scan = None
        self.odom = None
        self.goal_distance = 5.0

        self.get_logger().info("env_node started (STABLE CONTROL MODE)")

    # --------------------
    # Callbacks
    # --------------------
    def scan_callback(self, msg):
        self.scan = msg

    def odom_callback(self, msg):
        self.odom = msg

    def action_callback(self, msg):
        if len(msg.data) == 2:
            self.latest_action = msg.data

    # --------------------
    # Main loop
    # --------------------
    def step(self):
        if self.scan is None or self.odom is None:
            return

        # --------------------
        # Build observation
        # --------------------
        observation = self.obs_builder.build_observation(
            self.scan, self.odom
        )

        obs_msg = Float32MultiArray()
        obs_msg.data = observation.tolist()
        self.obs_pub.publish(obs_msg)

        # --------------------
        # Base motion (safe default)
        # --------------------
        linear = 0.25
        angular = 0.0

        # PPO override
       # if self.latest_action is not None:
        #    linear = float(self.latest_action[0])
         #   angular = float(self.latest_action[1])

        # --------------------
        # Safety clamp
        # --------------------
        valid_ranges = [r for r in self.scan.ranges if r > 0.0]
        min_range = min(valid_ranges) if valid_ranges else float('inf')

     #   if min_range < 0.06:
      #      linear = 0.0
       #     angular = 0.6

        linear = max(0.0, min(linear, 0.4))
        angular = max(-1.0, min(angular, 1.0))

        # --------------------
        # Publish Twist
        # --------------------
        cmd = TwistStamped()
        cmd.header.stamp = self.get_clock().now().to_msg()
        cmd.twist.linear.x = linear
        cmd.twist.angular.z = angular
        self.cmd_pub.publish(cmd)

        # --------------------
        # Goal progress
        # --------------------
        self.goal_distance = max(0.0, self.goal_distance - 0.002)

        # --------------------
        # Reward & termination
        # --------------------
        reward = self.reward_fn.compute(
            scan_msg=self.scan,
            odom_msg=self.odom,
            goal_distance=self.goal_distance,
            goal_reached=False,
        )

        done, reason = self.termination_checker.check(
            scan_msg=self.scan,
            goal_distance=self.goal_distance,
        )

        self.get_logger().info(
            f"reward={reward:.3f} | min_range={min_range:.2f} | done={done}"
        )

        if done:
            self.get_logger().warn(f"Episode done: {reason}")
            self.reward_fn.reset()
            self.termination_checker.reset()
            self.goal_distance = 5.0


def main(args=None):
    rclpy.init(args=args)
    node = EnvNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
