import os
import rclpy
from rclpy.node import Node
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np

from std_msgs.msg import Float32MultiArray, Float32


# --------------------
# PPO Policy Network
# --------------------
class PolicyNet(nn.Module):
    def __init__(self, obs_dim, act_dim):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(obs_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, act_dim),
            nn.Tanh()
        )

    def forward(self, x):
        return self.net(x)


# --------------------
# PPO Trainer Node
# --------------------
class PPOTrainer(Node):
    def __init__(self):
        super().__init__('ppo_trainer')

        # MUST match observation.py
        self.obs_dim = 26
        self.act_dim = 2

        # Model save path
        self.model_path = os.path.expanduser(
            '~/rosi_rl_ws/trained_models/ppo_policy_final.pth'
        )
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)

        self.policy = PolicyNet(self.obs_dim, self.act_dim)
        self.optimizer = optim.Adam(self.policy.parameters(), lr=3e-4)

        # Training buffers
        self.obs_buffer = []
        self.reward_buffer = []
        self.log_prob_buffer = []

        self.gamma = 0.99
        self.update_every = 200
        self.step_count = 0

        self.current_reward = 0.0
        self.episode_reward = 0.0

        # Subscribers
        self.obs_sub = self.create_subscription(
            Float32MultiArray,
            '/ppo/observation',
            self.obs_callback,
            10
        )

        self.reward_sub = self.create_subscription(
            Float32,
            '/ppo/reward',
            self.reward_callback,
            10
        )

        # Publisher
        self.action_pub = self.create_publisher(
            Float32MultiArray,
            '/ppo/action',
            10
        )

        self.get_logger().info("PPO trainer started (TRAINING MODE)")

    # --------------------
    # Reward callback
    # --------------------
    def reward_callback(self, msg):
        self.current_reward = msg.data

    # --------------------
    # Observation callback
    # --------------------
    def obs_callback(self, msg):
        obs = np.array(msg.data, dtype=np.float32)

        if obs.shape[0] != self.obs_dim:
            self.get_logger().warn("Observation size mismatch")
            return

        obs_tensor = torch.tensor(obs).unsqueeze(0)

        # Forward pass
        mean_action = self.policy(obs_tensor)
        dist = torch.distributions.Normal(mean_action, 0.1)
        action = dist.sample()
        log_prob = dist.log_prob(action).sum()

        action_np = action.detach().numpy()[0]

        # ✅ FIX: clamp action for stable motion
        action_np = np.clip(action_np, [-0.2, -1.0], [0.2, 1.0])

        # Publish action
        action_msg = Float32MultiArray()
        action_msg.data = action_np.tolist()
        self.action_pub.publish(action_msg)

        # Store transition
        self.obs_buffer.append(obs_tensor)
        self.reward_buffer.append(self.current_reward)
        self.log_prob_buffer.append(log_prob)

        self.episode_reward += self.current_reward
        self.step_count += 1

        # Update policy
        if self.step_count % self.update_every == 0:
            self.update_policy()
            self.get_logger().info(
                f"Policy updated | episode_reward={self.episode_reward:.2f}"
            )
            self.episode_reward = 0.0

    # --------------------
    # PPO-style update
    # --------------------
    def update_policy(self):
        returns = []
        G = 0.0

        for r in reversed(self.reward_buffer):
            G = r + self.gamma * G
            returns.insert(0, G)

        returns = torch.tensor(returns)
        returns = (returns - returns.mean()) / (returns.std() + 1e-8)

        loss = 0.0
        for log_prob, Gt in zip(self.log_prob_buffer, returns):
            loss += -log_prob * Gt

        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        self.obs_buffer.clear()
        self.reward_buffer.clear()
        self.log_prob_buffer.clear()

    # --------------------
    # Save model on shutdown
    # --------------------
    def destroy_node(self):
        self.get_logger().info("Saving trained PPO policy before shutdown...")
        torch.save(self.policy.state_dict(), self.model_path)
        self.get_logger().info(f"Model saved to {self.model_path}")
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = PPOTrainer()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
