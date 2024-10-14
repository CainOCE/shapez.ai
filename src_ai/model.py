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
import time
import json
import random
import logging
import numpy as np
import tensorflow as tf
import keras
import matplotlib.pyplot as plt

# Configure logging
log = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s:%(levelname)s: %(message)s',
    datefmt="%H:%M:%S",
    handlers=[logging.StreamHandler()]
)

 # TODO include all types of pipes
DIRECTION_TO_COORD = {
    '↑' : (-1, 0),
    '→' : (0, 1),
    '↓' : (1, 0),
    '←' : (0, -1),
    '↖' : (-1, -1),
    '↗' : (-1, 1),
    '↘' : (1, 1),
    '↙' : (1, -1),
    '▲' : (-1, 0),
    '▶' : (0, 1),
    '▼' : (1, 0),
    '◀': (0, -1)
}


GOALS = [['CuCuCuCu', 30]] # currently only level 1

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
        self.version = "0.5.0"
        self.state_machine = "ONLINE"
        self.episode_time = time.time()

        # The current state values
        self.pre_state = []
        self.post_state = []
        self.region = None
        self.action_space = None
        self.num_actions = 0
        self.queued_action = None

        # Model Training Factors
        self.seed = seed
        self.optimiser = keras.optimizers.Adam(learning_rate=0.0001)
        self.episodes = 0
        self.max_episodes = 30
        self.max_frames = 10000
        self.running_reward = 0
        self.episode_reward = 0
        self.frames = 0
        self.reward_goal = 10000 # reward total to stop training, right now set so hopefully stops from episodes

        # Chosen Hyperparameters
        self.gamma = 0.99
        self.epsilon = 1.0
        self.epsilon_min = 0.1
        self.epsilon_max = 1.0
        self.epsilon_interval = self.epsilon_max - self.epsilon_min
        self.batch_size = 32

        # Training Values
        self.epsilon_random_frames = 2500  # Random Action Frames
        self.epsilon_greedy_frames = 1000000.0  # Exploration Frames
        self.max_memory_length = 100  # Maximum replay length
        self.update_after_actions = 5  # Train Model every X Actions
        self.update_target_network = 5000  # Network Update Target
        self.loss_function = keras.losses.Huber()  # huber loss for stability

        # Experience replay buffers
        self.action_history = []
        self.state_history = []
        self.state_next_history = []
        self.goal_history = []
        self.rewards_history = []
        self.episode_reward_history = []

        # Build the models
        self.model = self.create_q_model()
        self.target = self.create_q_model()

    def get_state_machine(self):
        """ Returns the current state in the state machine. """
        return self.state_machine

    def create_q_model(self):
        """ Creates a Deep Q Style Model as seen in the deepmind paper. """
        # TODO -- fix this below, grab it dynamically
        num_actions = 8064
        self.num_actions = num_actions

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
                keras.layers.Dense(num_actions, activation="linear"),
            ]
        )

    def _get_training_status(self):
        """ Utility:  Gets the current training status. """
        e, e_max = (self.episodes, self.max_episodes)
        f, f_max = (self.frames, self.max_frames)
        a = str(self.queued_action).ljust(20)
        t = round(time.time() - self.episode_time, 3)
        return f" -> Training ({t})s:  Ep {e}|{e_max}, Fr {f}|{f_max}, Ac {a}"

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
            self.action_space = game.get_action_space()
            self.num_actions = len(self.action_space)
            print(f" -> Training Request:  {self.num_actions} action space")
            self.episode_reward = 0
            self.state_machine = "EPISODE"
            return None

        # 2.  Episode
        if self.get_state_machine() == "EPISODE":
            self.episodes += 1
            self.episode_time = time.time()

            # Add some boolean condition checks
            solved = self.running_reward >= self.reward_goal
            capped = self.episodes > self.max_episodes

            # Stop the episode
            if (solved or capped):
                self.episodes -= 1
                print(self._get_training_status())
                result = "Capped" if capped else "Solved"
                print(f" -> Training loop result in a '{result}' state")
                print(f" -> Episode trained in {self.episode_time} s")

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
                self.visualise()
                return None

            # Start the Episode
            self.frames = 0
            episode_reward = 1

            # Update running reward to check condition for solving
            self.episode_reward_history.append(episode_reward)
            self.episode_reward_history = self.episode_reward_history[-100:]
            self.running_reward = np.mean(self.episode_reward_history)
            self.state_machine = "PRE_FRAME"

            # reset history arrays
            # TODO -- cain are these in the right spot? meant to reset at start of each episode
            self.action_history = []
            self.state_history = []
            self.state_next_history = []
            self.goal_history = []
            self.rewards_history = []
            self.episode_reward_history = []

            return None

        # 3.  Pre-Frame:  Send an action to the frontend
        if self.get_state_machine() == "PRE_FRAME":
            # Reset if frames are finished
            if self.frames >= self.max_frames:
                self.state_machine = "EPISODE"
                return None

            # Execute a pre_frame.  eg get_action
            self.frames += 1

            # Generate gamestate for the frame
            self.pre_state = game

            # Select Action to return
            action = self._select_action()
            self.queued_action = action
            # action -> {"type", "x", "y", "rotation"}
            # e.g. {"type": "Belt", "x": 2, "y": y, "rotation": 270}

            # Print Status Helper
            print(self._get_training_status(), end="\r")
            self.state_machine = "POST_FRAME"
            return self.get_queued_action()

        # X.  -> Client runs between these

        # 4.  Post-Frame:  Process returned frontend
        if self.get_state_machine() == "POST_FRAME":
            self.post_state = game

            # Validate the action by assigning a score.
            reward = self.validate()
            self.running_reward += reward

            # Log the events
            # self.log(self.pre_state, self.post_state, action, reward)

            # Periodically update the model between several actions
            if (not self.frames % self.update_after_actions and
                len(self.goal_history) > self.batch_size):
                self._model_update()

            # update the the target network with new weights
            if not self.frames % self.update_target_network:
                self.target.set_weights(self.model.get_weights())

            # Move to next frame.
            self.state_machine = "PRE_FRAME"
            return None

        return None

    def _model_update(self):
        """ Handles the periodic updates to the model. """
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
        masks = keras.ops.one_hot(action_sample, self.num_actions)

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
        return


    def _select_action(self):
        """ Select an action using an epsilon-greedy strategy. """
        action = None
        action_space = self.action_space
        eps = np.random.random()

        # Take Random or attempt prediction.
        if (self.frames < self.epsilon_random_frames or
            self.epsilon > np.random.rand(1)[0]):
            # Take random action
            action = random.choice(action_space)
        else:
            # Predict action Q-Value from Environment
            region = self.pre_state.get_region_in_play()
            state_tensor = keras.ops.convert_to_tensor(region)
            state_tensor = keras.ops.expand_dims(state_tensor, 0)

            # Take best action
                # TODO Adjust actions by weights
                # TODO how do action probs change as action space changes
            action_probs = self.model(state_tensor, training=False)
            action = keras.ops.argmax(action_probs[0]).numpy()

        # Decay probability of taking random action
        self.epsilon -= self.epsilon_interval / self.epsilon_greedy_frames
        self.epsilon = max(self.epsilon, self.epsilon_min)

        # Split action back to variables
        x, y, rot, action = action.split("|")
        action = {
            "type": action,
            "x": int(x)-4, "y": int(y)-4,
            "rotation": int(rot)
        }
        return action

    def get_queued_action(self):
        """ Returns the queued action from the model and removes it. """
        action = self.queued_action
        self.queued_action = None
        return action

    # reward function -- very important for performance
     # things to check for: (using random numbers)
        # -- im scared to make rewards for non immediate goals so model does not find some hack
        # - produce goal shape (+1)
        # - produce future goal shape (+0.00001)
        # - belts connecting (+0.0001)
        # - belts connecting to hub (+0.0001)
        # - plus more... idk, could add heps here dpends how complex we want this method to be

    def validate(self):
        """ Heuristic scoring of the current model action.
            \"Reward Function\"
        """
        score = 0

        # Generate the regions of interest
        pre_region = self.pre_state.get_region_in_play()
        post_region = self.post_state.get_region_in_play()

        # Pull out the relevant items
        item, required = self.pre_state.get_goal()
        stored_pre = self.pre_state.get_stored_amount(item)
        stored_post = self.post_state.get_stored_amount(item)
        gained = stored_post - stored_pre

        # Did we gain the required item?:
        score += gained * 0.1

        # Did we produce a future goal shape? 

        # Checking elements per tile in the region
        for y, row in enumerate(pre_region):
            for x, _ in enumerate(row):

                # Are Miners on a resource?
                if post_region[y][x] in "▲▶▼◀" and pre_region[y][x] in "rgbX":
                    score += 0.01 
                
                # reduce score for miner not on resource
                if post_region[y][x] in "▲▶▼◀" and pre_region[y][x] not in "rgbX":
                    score -= 0.01

                # belt not on resource
                if post_region[y][x] in "↑→↓←↖↗↘↙" and pre_region[y][x] not in "rgbX":
                    score += 0.01 # small increase

                # Do belts connect logically?
                score += self.find_belt_chains(pre_region, post_region) # only count belts that start on resource

                # Do belts lead to the hub? -- accounted for in find_belt_chains

                # neg reward for placing building over another building -- dont think its neccessary 

        return score
    
    # search through board and find belt chains
    def find_belt_chains(self, pre, post):
        # return some score value
        # longer chains give more rewards up to distance to hub (lets approximate @ region radius)
        ideal_belt_len = len(post)//2 
        # score_distance = np.exp(1/5*(d - ideal_belt_len)**2)

        # construct belt chains
        self.belt_chains = []
        self.visited_cells = set()
        i = 0
        for y, row in enumerate(post):
            for x, _ in enumerate(row):
                token = post[y][x]
                if post[y][x] in "▲▶▼◀" and pre[y][x] in "rgbX":
                    self.belt_chains.append([])
                    self.find_chain_recursively((y, x), post, token, i)
                    i += 1
                self.visited_cells.add((y, x))

        # apply distance modifier to all belts
        score = 0
        for belt in self.belt_chains:
            hub = belt.pop(-1) # remove last element, if 'H' --> hub, add multiplier, else '0'
            belt_length = len(belt)
            # random gaussian i made to give score, will refine with testing
            score += 0.5 * np.exp(1 / 8 * (belt_length - ideal_belt_len) ** 2) 
            
            if hub == 'H':
                score += 1 


        return score 
    
    # recursive function to find a belt chain
    def find_chain_recursively(self, coords, post, token, i):
        # coords - current (y, x)
        # token - current token
        # i - current chain index in belt chain
        direction = DIRECTION_TO_COORD[token]
        self.belt_chains[i].append(coords)
        next_coords = [sum(jj) for jj in zip(coords, direction)]
        if next_coords not in self.visited_cells:
            self.visited_cells.add(coords)
            next_token = post[next_coords]
            # TODO include all types of pipes
            if token in "↑→↓←↖↗↘↙":
                self.find_chain_recursively(next_coords, post, next_token, i+ 1)
            else:
                if post[next_coords] == "H": # if hub add 'H' at end of array
                    self.belt_chains[i].append('H')
                else:
                    self.belt_chains[i].append('0')


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
            # del self.rewards_history[:1] # keep reward history for visualisation
            del self.goal_history[:1]

    def visualise(self):
        steps = np.linspace(0, len(self.rewards_history), len(self.rewards_history))
        plt.plot(steps, self.reward_history)
        plt.xlabel('steps')
        plt.ylabel('reward')
        plt.title('reward through time of last training episode')
        plt.show()


if __name__ == "__main__":
    print("Please call this module as a dependency or import.")