# -*- coding: utf-8 -*-
"""
Created on Tue Aug 13, 2024 at 09:55:41

@author: Cain Bruhn-Tanzer
"""

import os
import keras
import gymnasium
import numpy as np
import tensorflow as tf

from keras import layers
from gymnasium.wrappers import AtariPreprocessing, FrameStack

os.environ["KERAS_BACKEND"] = "tensorflow"


class Model:
    """ An abstract model class for AI development. """

    def __init__(self):
        self.alive = True
        self.name = "AbstractModel"

    def is_alive(self):
        """ Returns whether model is running. """
        return self.alive

    def get_name(self):
        """ Returns the name of the current model. """
        return self.name

    def step(self):
        """ Advances the model one step. """
        return True


class Overseer(Model):
    """ Model for optimising higher level logistics networks. """

    def __init__(self, seed=1234):
        super().__init__()
        self.name = "Overseer"
        self.seed = seed


class Architect(Model):
    """ Model for designing tight-packed, 'tall' sub-unit factory layouts. """

    def __init__(self):
        super().__init__()
        self.name = "Architect"


class RhysArchitect(Model):
    """ Model for designing tight-packed, 'tall' sub-unit factory layouts. """

    def __init__(self, seed=42):
        super().__init__()
        self.name = "Architect"

        # Setup the Environment
        self.seed = seed
        self.env = gymnasium.make("BreakoutNoFrameskip-v4")
        # , render_mode="human")
        self.env = AtariPreprocessing(self.env)
        self.env = FrameStack(self.env, 4)
        self.env.seed(self.seed)
        self.num_actions = 4
        self.action_space = [1, 2, 3]

        # Chosen Hyperparameters
        self.gamma = 0.99
        self.epsilon = 1.0
        self.epsilon_min = 0.1
        self.epsilon_max = 1.0
        self.epsilon_interval = self.epsilon_max - self.epsilon_min
        self.batch_size = 32
        self.max_steps_per_episode = 10000
        self.max_episodes = 10

        # Create the Deep Q Models
        self.q_model = self.create_q_model()
        self.q_model_target = self.create_q_model()
        self.optimiser = keras.optimizers.Adam(learning_rate=0.0001)

        # Experience replay buffers
        self.action_history = []
        self.state_history = []
        self.state_next_history = []
        self.rewards_history = []
        self.done_history = []
        self.episode_reward_history = []
        self.running_reward = 0
        self.episode_count = 0
        self.frame_count = 0

        # Training Values
        self.epsilon_random_frames = 50000  # Random Action Frames
        self.epsilon_greedy_frames = 1000000.0  # Exploration Frames
        self.max_memory_length = 100  # Maximum replay length
        # TODO:  Deepmind Suggests 100,000 memory max, significant memory usage
        self.update_after_actions = 4  # Train Model every X Actions
        self.update_target_network = 10000  # Network Update Target
        self.loss_function = keras.losses.Huber()  # huber loss for stability

    def create_q_model(self):
        """ Creates a Deep Q Style Model as seen in the deepmind paper. """
        # See https://keras.io/examples/rl/deep_q_network_breakout/
        return keras.Sequential(
            [
                layers.Lambda(
                    lambda tensor: keras.ops.transpose(tensor, [0, 2, 3, 1]),
                    output_shape=(84, 84, 4),
                    input_shape=(4, 84, 84),
                ),
                # Convolutions on the frames on the screen
                layers.Conv2D(
                    32, 8, strides=4,
                    activation="relu",
                    input_shape=(4, 84, 84)
                ),
                layers.Conv2D(64, 4, strides=2, activation="relu"),
                layers.Conv2D(64, 3, strides=1, activation="relu"),
                layers.Flatten(),
                layers.Dense(512, activation="relu"),
                layers.Dense(self.num_actions, activation="linear"),
            ]
        )

    def train(self):
        """ Begins the model training loop. (episode) """

        # Setup our training episode
        observation, _ = self.env.reset()
        state = np.array(observation)
        episode_reward = 0

        while True:
            for timestep in range(1, self.max_steps_per_episode):
                self.frame_count += 1
                done = self._step(state)
                if done:
                    break

            # Update running reward to check condition for solving
            self.episode_reward_history.append(episode_reward)
            if len(self.episode_reward_history) > 100:
                del self.episode_reward_history[:1]
            running_reward = np.mean(self.episode_reward_history)

            self.episode_count += 1

            # Condition to consider the task solved
            if running_reward > 40:
                print(f"Solved at episode {self.episode_count}!")
                break

            # Maximum number of episodes reached
            if (
                self.max_episodes > 0 and
                self.episode_count >= self.max_episodes
            ):
                print(f"Stopped at episode {self.episode_count}!")
                break
        return

    def _step(self, state):
        """ Advances the model one step. """
        super().step()

        # Use epsilon-greedy for exploration
        if (
            self.frame_count < self.epsilon_random_frames or
            self.epsilon > np.random.rand(1)[0]
        ):
            # Take random action
            action = np.random.choice(self.num_actions)
        else:
            # Predict action Q-values
            # From environment state
            state_tensor = keras.ops.convert_to_tensor(state)
            state_tensor = keras.ops.expand_dims(state_tensor, 0)
            action_probs = self.q_model(state_tensor, training=False)
            # Take best action
            action = keras.ops.argmax(action_probs[0]).numpy()

        # Decay probability of taking random action
        self.epsilon -= self.epsilon_interval / self.epsilon_greedy_frames
        self.epsilon = max(self.epsilon, self.epsilon_min)

        # Apply the sampled action in our environment
        state_next, reward, done, _, _ = self.env.step(action)
        if reward > 0 or done:
            print(reward)
            print(done)
        state_next = np.array(state_next)

        self.running_reward += reward

        # Save actions and states in replay buffer
        self.action_history.append(action)
        self.state_history.append(state)
        self.state_next_history.append(state_next)
        self.done_history.append(done)
        self.rewards_history.append(reward)
        state = state_next

        # Update every fourth frame and once batch size is over 32
        if (
            self.frame_count % self.update_after_actions == 0 and
            len(self.done_history) > self.batch_size
        ):
            # Get indices of samples for replay buffers
            indices = np.random.choice(
                range(len(self.done_history)),
                size=self.batch_size
            )

            # Using list comprehension to sample from replay buffer
            state_sample = np.array([self.state_history[i] for i in indices])
            state_next_sample = np.array(
                [self.state_next_history[i] for i in indices]
            )
            rewards_sample = [self.rewards_history[i] for i in indices]
            action_sample = [self.action_history[i] for i in indices]
            done_sample = keras.ops.convert_to_tensor(
                [float(self.done_history[i]) for i in indices]
            )

            # Build the updated Q-values for the sampled future states
            # Use the target model for stability
            future_rewards = self.q_model_target.predict(state_next_sample)
            # Q value = reward + discount factor * expected future reward
            updated_q_values = rewards_sample + self.gamma * keras.ops.amax(
                future_rewards, axis=1
            )

            # If final frame set the last value to -1
            updated_q_values = updated_q_values*(1-done_sample) - done_sample

            # Create a mask so we only calculate loss on the updated Q-values
            masks = keras.ops.one_hot(action_sample, self.num_actions)

            with tf.GradientTape() as tape:
                # Train the model on the states and updated Q-values
                q_values = self.q_model(state_sample)

                # Apply the masks to the Q-values to get the Q-value for
                # action taken
                q_action = keras.ops.sum(
                    keras.ops.multiply(q_values, masks), axis=1
                )

                # Calculate loss between new Q-value and old Q-value
                loss = self.loss_function(updated_q_values, q_action)

            # Backpropagation
            grads = tape.gradient(loss, self.q_model.trainable_variables)
            self.optimiser.apply_gradients(
                zip(grads, self.q_model.trainable_variables)
            )

        if self.frame_count % self.update_target_network == 0:
            # update the the target network with new weights
            self.q_model_target.set_weights(self.q_model.get_weights())
            # Log details
            # template = "running reward: {:.2f} at episode {}, frame count {}"
            # print(template.format(
            #     running_reward,
            #     episode_count,
            #     self.frame_count)
            # )
            # TODO Reconstitute this print statement

        # Limit the state and reward history
        if len(self.rewards_history) > self.max_memory_length:
            del self.rewards_history[:1]
            del self.state_history[:1]
            del self.state_next_history[:1]
            del self.action_history[:1]
            del self.done_history[:1]

        return done


if __name__ == "__main__":
    print("Please call this module as a dependency or import.")
