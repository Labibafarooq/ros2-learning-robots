import rclpy
from rclpy.node import Node
import numpy as np
from std_msgs.msg import Float32MultiArray


class PPOTrainer(Node):
    """
    PPO Trainer (Action Publisher Mode)
    """

    def __init__(self):
        super().__init__('ppo_trainer')

        # --------------------
        # Subscribers
        # --------------------
        self.latest_observation = None
        self.obs_sub = self.create_subscription(
            Float32MultiArray,
            '/ppo/observation',
            self.obs_callback,
            10
        )

        # --------------------
        # Action publisher (NEW)
        # --------------------
        self.action_pub = self.create_publisher(
            Float32MultiArray,
            '/ppo/action',
            10
        )

        # Dimensions
        self.obs_dim = 26
        self.action_dim = 2

        # Rollout storage (kept for later learning)
        self.observations = []
        self.actions = []
        self.rewards = []
        self.dones = []

        self.max_steps = 200
        self.step_count = 0

        self.get_logger().info("PPO Trainer started (ACTION PUBLISH MODE)")

        # Timer
        self.timer = self.create_timer(0.1, self.rollout_step)

    # --------------------
    # Callbacks
    # --------------------
    def obs_callback(self, msg):
        self.latest_observation = np.array(msg.data)

    # --------------------
    # Rollout
    # --------------------
    def rollout_step(self):
        if self.latest_observation is None:
            return

        obs = self.latest_observation

        # 🔹 Random action (still baseline)
        action = np.random.uniform(
            low=[0.0, -0.5],
            high=[0.3, 0.5]
        )

        # Publish action to env_node
        action_msg = Float32MultiArray()
        action_msg.data = action.tolist()
        self.action_pub.publish(action_msg)

        # Dummy reward (env_node computes real one)
        reward = 0.0
        done = False

        # Store rollout
        self.observations.append(obs)
        self.actions.append(action)
        self.rewards.append(reward)
        self.dones.append(done)

        self.step_count += 1

        self.get_logger().info(
            f"Rollout step {self.step_count} | action={action}"
        )

        if self.step_count >= self.max_steps:
            self.reset_episode()

    def reset_episode(self):
        self.observations.clear()
        self.actions.clear()
        self.rewards.clear()
        self.dones.clear()
        self.step_count = 0


def main(args=None):
    rclpy.init(args=args)
    node = PPOTrainer()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
