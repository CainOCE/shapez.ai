import os
import keras
import numpy as np
import tensorflow as tf
from game import shapezGym
import time

from keras import layers

os.environ["KERAS_BACKEND"] = "tensorflow"

# hyperparameters
gamma = 0.99  # Discount factor for past rewards
epsilon = 1.0  # Epsilon greedy parameter
epsilon_min = 0.1  # Minimum epsilon greedy parameter
epsilon_max = 1.0  # Maximum epsilon greedy parameter
epsilon_interval = (
    epsilon_max - epsilon_min
)  # Rate at which to reduce chance of random action being taken
batch_size = 32  # Size of batch taken from replay buffer
max_steps_per_episode = 10000
max_episodes = 10  # Limit training episodes, will run until solved if smaller than 1

optimiser = keras.optimizers.Adam(learning_rate=0.0001)

# Experience replay buffers
action_history = []
state_history = []
state_next_history = []
rewards_history = []
goal_history = []
episode_reward_history = []
running_reward = 0
episode_count = 0
frame_count = 0
# Number of frames to take random action and observe output
epsilon_random_frames = 50000
# Number of frames for exploration
epsilon_greedy_frames = 1000000.0
# Maximum replay length
# Note: The Deepmind paper suggests 1000000 however this causes memory issues
max_memory_length = 100000
# Train the model after 4 actions
update_after_actions = 4
# How often to update the target network
update_target_network = 10000
# Using huber loss for stability
loss_function = keras.losses.Huber()
# buildings available to place in game -- start simple
buildings = ['empty', 'belt', 'extractor']
# environment for game
game = shapezGym(buildings)
# available actions for model
actions = game.action_space #


####
"""
example from "https://keras.io/examples/rl/deep_q_network_breakout/"

model framework, initialise layers and weights
"""
def create_q_model():
    # Network defined by the Deepmind paper
    ## start with this standard model, look to change in future after testing
    return keras.Sequential(
        [
            layers.Lambda(
                lambda tensor: keras.ops.transpose(tensor, [0, 2, 3, 1]),
                output_shape=(84, 84, 4),
                input_shape=(4, 84, 84),
            ),
            # Convolutions on the frames on the screen
            layers.Conv2D(32, 8, strides=4, activation="relu", input_shape=(4, 84, 84)),
            layers.Conv2D(64, 4, strides=2, activation="relu"),
            layers.Conv2D(64, 3, strides=1, activation="relu"),
            layers.Flatten(),
            layers.Dense(512, activation="relu"),
            layers.Dense(len(actions), activation="linear"),
        ]
    )

"""
saves the given model to a text file
"""
def save_model(model):
    model.save('model'+str(time.time())+'.h5')

"""
loads the given text file into a model
"""
def load_model(file):
    return load_model(file)

"""
save history of actions to a text file

for reproducibility and visualisation later
"""
def save_actions(seed, actions_history):
    fileName = "actions" + str(time.time()) + ".txt"
    file = open(fileName, 'w')
    file.write(str(seed) + "\n")
    for a in actions_history:
        file.write(str(a) + "\n")
    file.close()


"""
check if model has completed training

will need some tweaking to discern whether the current running reward is high enough
"""
def check_completion():
    if running_reward > 40:  # Condition to consider the task solved
            print("Solved at episode {}!".format(episode_count))

    if (max_episodes > 0 and episode_count >= max_episodes):  # Maximum number of episodes reached
            print("Stopped at episode {}!".format(episode_count))


"""
instatiation and training of model

based on a "homemade" environemnt of shapez defined in game.py shapezGym class
"""
def bob():
    # actions -- a dictionary containing valid actions

    model = create_q_model() # training model????
    model_target = create_q_model() # testing model????
    num_actions = game.action_space # a gym.Discrete class

    ## do we want observatino space to the be the gym.Box class???

    # train model
    while not check_completion:
        ## restart game -- fresh start of training episode
        seed, current_state = game.reset() # could make this reset to higher level for different training?
        episode_reward = 0

        for timestep in range(1, max_steps_per_episode):
            frame_count+=1

            if frame_count < epsilon_random_frames or epsilon > np.random.rand(1)[0]:
                action = np.random.choice(num_actions)
            else:
                # Predict action Q-values
                # From environment state
                state_tensor = keras.ops.convert_to_tensor(current_state)
                state_tensor = keras.ops.expand_dims(state_tensor, 0)
                action_probs = model(state_tensor, training=False)
                # Take best action
                action = keras.ops.argmax(action_probs[0]).numpy()

            # Decay probability of taking random action
            epsilon -= epsilon_interval / epsilon_greedy_frames
            epsilon = max(epsilon, epsilon_min)

            # Apply the sampled action in our environment
            state_next, reward, goal_reached = game.step(action)
            ##### need to finish game environment

            state_next = np.array(state_next)

            episode_reward += reward

            # Save actions and states in replay buffer
            action_history.append(action)
            state_history.append(current_state)
            goal_history.append(goal_reached)
            state_next_history.append(state_next)
            rewards_history.append(reward)
            current_state = state_next

            # Update every fourth frame and once batch size is over 32
            if frame_count % update_after_actions == 0 and len(goal_history) > batch_size:
                # Get indices of samples for replay buffers
                indices = np.random.choice(range(len(goal_history)), size=batch_size)

                # Using list comprehension to sample from replay buffer
                state_sample = np.array([state_history[i] for i in indices])
                state_next_sample = np.array([state_next_history[i] for i in indices])
                rewards_sample = [rewards_history[i] for i in indices]
                action_sample = [action_history[i] for i in indices]
                goal_sample = keras.ops.convert_to_tensor(
                    [float(goal_history[i]) for i in indices]
                )

                # Build the updated Q-values for the sampled future states
                # Use the target model for stability
                future_rewards = model_target.predict(state_next_sample)
                # Q value = reward + discount factor * expected future reward
                updated_q_values = rewards_sample + gamma * keras.ops.amax(
                    future_rewards, axis=1
                )

                # If final frame set the last value to -1
                updated_q_values = updated_q_values * (1 - goal_sample) - goal_sample

                # Create a mask so we only calculate loss on the updated Q-values
                masks = keras.ops.one_hot(action_sample, num_actions)

                with tf.GradientTape() as tape:
                    # Train the model on the states and updated Q-values
                    q_values = model(state_sample)

                    # Apply the masks to the Q-values to get the Q-value for action taken
                    q_action = keras.ops.sum(keras.ops.multiply(q_values, masks), axis=1)
                    # Calculate loss between new Q-value and old Q-value
                    loss = loss_function(updated_q_values, q_action)

                # Backpropagation
                grads = tape.gradient(loss, model.trainable_variables)
                optimiser.apply_gradients(zip(grads, model.trainable_variables))

            if frame_count % update_target_network == 0:
                # update the the target network with new weights
                model_target.set_weights(model.get_weights())
                # Log details
                template = "running reward: {:.2f} at episode {}, frame count {}"
                print(template.format(running_reward, episode_count, frame_count))

            # Limit the state and reward history
            if len(rewards_history) > max_memory_length:
                del rewards_history[:1]
                del state_history[:1]
                del goal_history[:1]
                del state_next_history[:1]
                #del action_history[:1] ### maybe keep action_history for reproductibility

        # Update running reward to check condition for solving
        episode_reward_history.append(episode_reward)
        if len(episode_reward_history) > 100:
            del episode_reward_history[:1]
        running_reward = np.mean(episode_reward_history)

        episode_count += 1

    # training done -- save models, save action history
    save_model(model)
    save_model(model_target)
    save_actions(seed, action_history) # will only save




if __name__ == "__main__":
    print("Please call this module as a dependency or import.")


bob()
