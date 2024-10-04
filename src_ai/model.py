# -*- coding: utf-8 -*-
"""
Created on Tue Aug 13, 2024 at 09:55:41

@author: Cain Bruhn-Tanzer, Rhys Tyne
"""
import os
import sys

# Set environment flags before running imports.
os.environ["KERAS_BACKEND"] = "tensorflow"
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Supress INFO Logs

# pylint: disable=C0413
import json
from datetime import datetime
import numpy as np
import tensorflow as tf
import keras
import random

MODEL_STORAGE_DIRECTORY = "./src_ai/models"


class Model:
    """ An abstract model class for AI development. """

    def __init__(self):
        self.alive = True
        self.name = "AbstractModel"
        self.version = "0.0.0"
        self.model = {}

    def save(self, obj):
        """ Saves the current model as a JSON schema file. """
        os.makedirs(MODEL_STORAGE_DIRECTORY, exist_ok=True)
        folder = MODEL_STORAGE_DIRECTORY
        name = self.name
        version = self.version
        dtime = datetime.now().strftime("%Y-%M-%D_%H_%M_%S")
        path = f"{folder}/{name}_{version}_{dtime}.json"
        with open(path, 'w', encoding='utf-8') as json_file:
            json.dump(obj, json_file, indent=4)

    def load(self, file):
        """ Loads a model saved as a JSON schema file. """
        with open(file, 'r', encoding='utf-8') as json_file:
            self.model = json.load(json_file)

    def is_alive(self):
        """ Returns whether model is running. """
        return self.alive

    def get_name(self):
        """ Returns the name of the current model. """
        return self.name

    def train(self, game):  # pylint: disable=W0613
        """ Advances the model multiple steps to complete a training cycle. """
        return None

    def validate(self):
        """ Checks a given solution and assigns points to it. """
        return None

    def _step(self, state):  # pylint: disable=W0613
        """ Advances the model one step. """
        return True

    def query(self, scenario):  # pylint: disable=W0613
        """ Queries the Model for a solution to a specific scenario. """
        return None


class Overseer(Model):
    """ Model for optimising higher level logistics networks.

    Requirements:
        - Must be able to draw and optimise networks between existing nodes
            where nodes is a sub-factory layout.
        - Must maintain a collection of possible node choices generated by
            architects.
    """

    def __init__(self, seed=1234):
        super().__init__()
        self.name = "Overseer"
        self.version = "0.1.0"
        self.seed = seed
        self.nodes = []

    def query(self, scenario):
        """ Returns a single action given a scenario.
            - Build a response from the overseer
            - Add in a few queries of Architect if necessary.
        """
        # Trigger something in the model based on the gameState
        temp_response = []

        # Place a strip of belts
        temp_response.extend([
            {"type": "Belt", "x": 2, "y": y, "rotation": 270}
            for y in range(-2, 2)]
        )

        # Place a strip of readers
        temp_response.extend([
            {"type": "Reader", "x": 3, "y": y, "rotation": 270}
            for y in range(-2, 2)]
        )

        # Place a strip of miners
        temp_response.extend([
            {"type": "Miner", "x": 4, "y": y, "rotation": 270}
            for y in range(-2, 2)]
        )
        temp_response.extend([
            {"type": "Miner", "x": 5, "y": y, "rotation": 270}
            for y in range(-2, 1)]
        )
        temp_response.extend([
            {"type": "Miner", "x": 6, "y": y, "rotation": 270}
            for y in range(-2, 0)]
        )
        temp_response.extend([
            {"type": "Miner", "x": 7, "y": -2, "rotation": 270}
        ])

        return temp_response


class Architect(Model):
    """ Model for designing sub-unit factory layouts. """

    def __init__(self, seed=42):
        super().__init__()
        self.name = "RhysArchitect"
        self.version = "0.3.0"
        self.seed = seed
        self.model = {}
        self.target = {}
        self.optimiser = keras.optimizers.Adam(learning_rate=0.0001)

        # Chosen Hyperparameters
        self.gamma = 0.99
        self.epsilon = 1.0
        self.epsilon_min = 0.1
        self.epsilon_max = 1.0
        self.epsilon_interval = self.epsilon_max - self.epsilon_min
        self.batch_size = 32
        self.max_steps_per_episode = 10000
        self.max_episodes = 100

        # Training Values
        self.epsilon_random_frames = 50000  # Random Action Frames
        self.epsilon_greedy_frames = 1000000.0  # Exploration Frames
        self.max_memory_length = 100  # Maximum replay length
        # TODO:  Deepmind Suggests 100,000 memory max, significant memory usage
        self.update_after_actions = 4  # Train Model every X Actions
        self.update_target_network = 10000  # Network Update Target
        self.loss_function = keras.losses.Huber()  # huber loss for stability

        # Experience replay buffers
        self.action_history = []
        self.state_history = []
        self.state_next_history = []
        self.goal_history = []
        self.rewards_history = []
        self.episode_reward_history = []

        # Episode Values
        self.running_reward = 0
        self.episodes = 0
        self.frames = 0

    def create_q_model(self, actions):
        """ Creates a Deep Q Style Model as seen in the deepmind paper. """
        # See https://keras.io/examples/rl/deep_q_network_breakout/
        return keras.Sequential(
            [
                keras.layers.Input(shape=(4, 84, 84)),
                keras.layers.Lambda(
                    lambda tensor: keras.ops.transpose(tensor, [0, 2, 3, 1]),
                    output_shape=(84, 84, 4),
                ),
                # Convolutions on the frames on the screen
                keras.layers.Conv2D(32, 8, strides=4, activation="relu",),
                keras.layers.Conv2D(64, 4, strides=2, activation="relu"),
                keras.layers.Conv2D(64, 3, strides=1, activation="relu"),
                keras.layers.Flatten(),
                keras.layers.Dense(512, activation="relu"),
                keras.layers.Dense(actions, activation="linear"),
            ]
        )

    def train(self, game):
        """ Begins the model training loop. (episode) """
        print("Training Architect Model:")

        # Key Game Values
        print(" -> Setting Key Values")
        seed = game.get_seed()
        action_space = game.get_all_actions()
        num_actions = len(action_space)

        # Create the Deep Q Models
        print(" -> Creating Deep Q Model & Target Model")
        self.model = self.create_q_model(len(action_space))
        self.target = self.create_q_model(len(action_space))

        # Begin the training loop "Episode"
        
        while not (
            (self.running_reward > 40) or (self.episodes >= self.max_episodes)):
            episode_reward = 0

            # Update Console Status
            status = f"{self.episodes} of {self.max_episodes}"
            sys.stdout.write(f"\r -> Training Episode... [{status}]")
            sys.stdout.flush()

            # Conduct X _steps() per episode.
            for _ in range(1, self.max_steps_per_episode):
                """
                things to check:
                - DO I NEED TO RESET ALL HYPERPARAMETERS TO ORIGINAL VALUES AT START OF EACH EPISODE????
                
                - HOW DOES MODEL RETURNS BEST ACTION? WHAT IS THE FORMAT?
                
                """

                self.frames += 1
                action = None # define action before use
                pos = None # position of action (pos = i * game.size + j)
                # Use epsilon-greedy for exploration
                if (self.frames < self.epsilon_random_frames or self.epsilon > np.random.rand(1)[0]):
                    # Take random action
                    possible_actions = game.get_possible_actions()
                    pos = np.random.randint(game.size**2)
                    action = random.choice(possible_actions[pos])
                else:
                    # Predict action Q-values
                    # From environment state
                    state_tensor = keras.ops.convert_to_tensor(state)
                    state_tensor = keras.ops.expand_dims(state_tensor, 0)
                    action_probs = self.model(state_tensor, training=False)
                    # Take best action
                    # _-_-_-_-------how do I need to adjust aciton_probs??? -----_-_-___-_---
                    # how is this aciton being returned? we need like (x, y, action)
                    action = keras.ops.argmax(action_probs[0]).numpy() 

                # Decay probability of taking random action
                self.epsilon -= self.epsilon_interval / self.epsilon_greedy_frames
                self.epsilon = max(self.epsilon, self.epsilon_min)

                # Apply the sampled action in our environment
                # TODO Apply the action in game or validate heuristically.

                reward = game.step(pos, action)

                state_next, reward, goal = (state, 0, 0)
                # state_next, reward, goal = game.validate()
                state_next = np.array(state_next)
                self.running_reward += reward

                # Save actions and states in replay buffer
                self.action_history.append(action)
                self.state_history.append(state)
                self.state_next_history.append(state_next)
                self.goal_history.append(goal)
                self.rewards_history.append(reward)
                state = state_next
                        
            self.frames = 0

            self.episodes += 1

            

            # Manually Reset the game for a training episode.
            # game.reset()  # TODO can we game.reset(lvl=1) to target train?
            seed = game.get_seed()
            state = game.get_region(-18, -18, 36, 36)

            
            # Update running reward to check condition for solving
            self.episode_reward_history.append(episode_reward)
            if len(self.episode_reward_history) > 100:
                del self.episode_reward_history[:1]
            self.running_reward = np.mean(self.episode_reward_history)

        # Report on outcome
        print("[SOLVED]" if self.episodes < self.max_episodes else "[CAPPED]")

        # Save our model and action history.
        print(" -> Saving Model:  ")
        # TODO Model and target won't serialize, discuss
        # self.save({
        #     "model": self.model,
        #     "target": self.target,
        #     "actions:": self.action_history
        # })

        return

    def _step(self, game, state, actions):
        """ Advances the model one step. """
        num_actions = len(actions)

        

        

        # Update every fourth frame and once batch size is over 32
        if (
            self.frames % self.update_after_actions == 0 and
            len(self.goal_history) > self.batch_size
        ):
            # Get indices of samples for replay buffers
            indices = np.random.choice(
                range(len(self.goal_history)), size=self.batch_size
            )

            # Using list comprehension to sample from replay buffer
            state_sample = np.array([self.state_history[i] for i in indices])
            state_next_sample = np.array(
                [self.state_next_history[i] for i in indices]
            )
            rewards_sample = [self.rewards_history[i] for i in indices]
            action_sample = [self.action_history[i] for i in indices]
            goal_sample = keras.ops.convert_to_tensor(
                [float(self.goal_history[i]) for i in indices]
            )

            # Build the updated Q-values for the sampled future states
            # Use the target model for stability
            future_rewards = self.target.predict(state_next_sample)
            # Q value = reward + discount factor * expected future reward
            updated_q_values = rewards_sample + self.gamma * keras.ops.amax(
                future_rewards, axis=1
            )

            # If final frame set the last value to -1
            updated_q_values = updated_q_values*(1-goal_sample) - goal_sample

            # Create a mask so we only calculate loss on the updated Q-values
            masks = keras.ops.one_hot(action_sample, num_actions)

            with tf.GradientTape() as tape:
                # Train the model on the states and updated Q-values
                q_values = self.model(state_sample)

                # Apply the masks to the Q-values to get the Q-value for
                # action taken
                q_action = keras.ops.sum(
                    keras.ops.multiply(q_values, masks), axis=1
                )

                # Calculate loss between new Q-value and old Q-value
                loss = self.loss_function(updated_q_values, q_action)

            # Backpropagation
            grads = tape.gradient(loss, self.model.trainable_variables)
            self.optimiser.apply_gradients(
                zip(grads, self.model.trainable_variables)
            )

        if self.frames % self.update_target_network == 0:
            # update the the target network with new weights
            self.target.set_weights(self.model.get_weights())
            # Log details
            template = "running reward: {:.2f} at episode {}, frame count {}"
            print(template.format(
                self.running_reward,
                self.episodes,
                self.frames)
            )

        # Limit the state and reward history
        if len(self.rewards_history) > self.max_memory_length:
            del self.state_history[:1]
            del self.state_next_history[:1]
            del self.rewards_history[:1]
            del self.goal_history[:1]

        return True


if __name__ == "__main__":
    print("Please call this module as a dependency or import.")
