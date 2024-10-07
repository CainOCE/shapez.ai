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
from datetime import datetime
import json
import random
import logging
import numpy as np
import tensorflow as tf
import keras

# Configure logging
log = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s:%(levelname)s: %(message)s',
    datefmt="%H:%M:%S",
    handlers=[logging.StreamHandler()]
)

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
        dtime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
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

    def _step(self, game):  # pylint: disable=W0613
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
        self.name = "Architect"
        self.version = "0.4.0"
        self.state_machine = "ONLINE"

        # The current state values
        self.region = None
        self.action_space = None  # Dict({ "f'{x}|{y}'": ["ABCD"], etc })
        self.num_actions = 0
        self.queued_action = None

        # Model Training Factors
        self.seed = seed
        self.model = {}
        self.target = {}
        self.optimiser = keras.optimizers.Adam(learning_rate=0.0001)
        self.episodes = 0
        self.max_episodes = 10   # TODO was 10
        self.max_frames = 20  # TODO was 10,000
        self.running_reward = 0
        self.episode_reward = 0
        self.frames = 0

        # Chosen Hyperparameters
        self.gamma = 0.99
        self.epsilon = 1.0
        self.epsilon_min = 0.1
        self.epsilon_max = 1.0
        self.epsilon_interval = self.epsilon_max - self.epsilon_min
        self.batch_size = 32

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

    def get_state_machine(self):
        """ Returns the current state in the state machine. """
        return self.state_machine

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

    def _get_training_status(self):
        """ Utility:  Gets the current training status. """
        if self.get_state_machine == "ONLINE":
            return "Not Training."
        e, e_max = (self.episodes, self.max_episodes)
        f, f_max = (self.frames, self.max_frames)
        a = str(self.queued_action).ljust(20)
        return f" -> Training:  Ep {e}|{e_max}, Fr {f}|{f_max}, Ac {a}"

    def train(self, game):
        """ Begins the model training state machine.

        NOTE: Frankly I hate that this is necessary, but keeping the two
              systems in lockstep is painful.

        1.  Train:  Sets the GameState as a region and action space.
        2.  Episode:  Starts an episode that triggers a reset on the client.
        3.  Pre-Frame:  Queues an action for the client to apply to the game.
            -> Client Runs Action for X Steps to generate new state for frame.
        4.  Post-Frame:  New state is validated.
        """

        # 1.  Train
        if self.get_state_machine() == "ONLINE":
            print(" -> Training Request")
            self.region = game.get_region(-18, -18, 36, 36)
            self.action_space = game.get_action_space(self.region)
            self.num_actions = len(self.action_space)

            print(" -> Setting Key Values")
            self.seed = game.get_seed()
            self.episode_reward = 0

            print(" -> Creating Deep Q Model & Target Model")
            self.model = self.create_q_model(self.num_actions)
            self.target = self.create_q_model(self.num_actions)
            self.state_machine = "EPISODE"
            return None

        # 2.  Episode
        if self.get_state_machine() == "EPISODE":
            self.episodes += 1

            # Add some boolean condition checks
            solved = self.running_reward >= 40
            capped = self.episodes > self.max_episodes

            # Stop the episode
            if (solved or capped):
                self.episodes -= 1
                print(self._get_training_status())
                result = "Capped" if capped else "Solved"
                print(f" -> Training loop result in a '{result}' state")

                # Save our model
                print(" -> Saving Model.")
                self.save({
                    "model": self.model.to_json(),
                    "target": self.target.to_json(),
                    "actions:": self.action_history
                })

                print(" -> Cleaning Episode State.")
                self.state_machine = "COMPLETE"
                self.episodes = 0
                print(" -> Training Complete.")
                self.state_machine = "ONLINE"
                return None

            # Start the Episode
            self.frames = 0
            episode_reward = 1

            # Update running reward to check condition for solving
            self.episode_reward_history.append(episode_reward)
            self.episode_reward_history = self.episode_reward_history[-100:]
            self.running_reward = np.mean(self.episode_reward_history)
            self.state_machine = "PRE_FRAME"
            return None

        # 3.  Pre-Frame
        if self.get_state_machine() == "PRE_FRAME":
            # Reset if frames are finished
            if self.frames >= self.max_frames:
                self.state_machine = "EPISODE"
                return None

            # Execute a pre_frame.  eg get_action
            self.frames += 1

            # Select Action to return
            action = self._select_action(self.action_space)
            self.queued_action = action
            # e.g. {"type": "Belt", "x": 2, "y": y, "rotation": 270}
            # action -> {"x", "y", "type", "rotation"}

            print(self._get_training_status(), end="\r")
            self.state_machine = "POST_FRAME"
            return self.get_queued_action()

        # X.  -> Client runs between these

        # 4.  Post-Frame
        if self.get_state_machine() == "POST_FRAME":
            # Do something with the result of the frame

            # 4.  Validate the action by assigning a score.
            # reward = self.validate(state)
            # self.running_reward += reward

            self.state_machine = "PRE_FRAME"
            return None

        return None

    def _step(self, game):
        """ Advances the model one step.
        Rhys Notes:
        - DO I NEED TO RESET ALL HYPERPARAMETERS TO ORIGINAL VALUES AT START
        OF EACH EPISODE????
        - i think we do need a state because thats how tensorflow works to use
        prebuilt methods
        """
        # 1.  Get state and action space from current GameState
        state = self.region

        # 2.  Choose available action for frame
        action = self._select_action(self.action_space)
        self.queued_action = action

        # 3.  Apply the action
        # state_next = game.step(self.queued_action)
        return

        # state_next = np.array(state_next)
        # state_next, reward, goal = (state, 0, 0)

        # 4.  Validate the action by assigning a score.
        reward = self.validate(state)
        self.running_reward += reward

        # 5.  Log the events
        self.log(state, state_next, action, reward, goal)

        # state = state_next
        # Update every fourth frame and once batch size is over 32
        if (self.frames % self.update_after_actions == 0 and
            len(self.goal_history) > self.batch_size):

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

        return

    def _select_action(self, action_space):
        """ Select an action using an epsilon-greedy strategy. """
        action = None

        # TODO Naive Random Implementation, fix for Epsilon Greedy
        position = random.choice(list(action_space.keys()))
        action = random.choice(action_space[position])
        direction = random.choice([0, 90, 180, 270])
        # Get direction from action

        return {position: action}

        # Take Random or attempt prediction.
        if (self.frames < self.epsilon_random_frames or
            self.epsilon > np.random.rand(1)[0]):
            # Take random action
            action = random.choice(action_space)
        else:
            # Predict action Q-Value from Environment
            state_tensor = keras.ops.convert_to_tensor(state)
            state_tensor = keras.ops.expand_dims(state_tensor, 0)
            action_probs = self.model(state_tensor, training=False)
                # TODO Adjust actions by weights
            # Take best action
            action = keras.ops.argmax(action_probs[0]).numpy()

        # Decay probability of taking random action
        self.epsilon -= self.epsilon_interval / self.epsilon_greedy_frames
        self.epsilon = max(self.epsilon, self.epsilon_min)

        return action

    def get_queued_action(self):
        """ Returns the queued action from the model and removes it. """
        action = self.queued_action
        self.queued_action = None
        return action

    # reward function -- very important for performance
    def validate(self, state):
        return 1
        # things to check for: (using random numbers)
        # -- im scared to make rewards for non immediate goals so model does not find some hack
        # - produce goal shape (+1)
        # - produce future goal shape (+0.00001)
        # - belts connecting (+0.0001)
        # - belts connecting to hub (+0.0001)
        # - plus more... idk, could add heps here dpends how complex we want this method to be

    def log(self, state, state_next, action, reward, goal):
        """ Updates the logged event history. """
        # Update the logs
        self.action_history.append(action)
        self.state_history.append(state)
        self.state_next_history.append(state_next)
        self.goal_history.append(goal)
        self.rewards_history.append(reward)

        # Limit the state and reward history
        if len(self.rewards_history) > self.max_memory_length:
            del self.state_history[:1]
            del self.state_next_history[:1]
            del self.rewards_history[:1]
            del self.goal_history[:1]


if __name__ == "__main__":
    print("Please call this module as a dependency or import.")
