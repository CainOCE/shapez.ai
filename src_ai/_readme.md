# Shapez.AI by Fish Obsessed

Teaching a python Deep Q Learning model to play the hit game shapez.io.

## Project Concept

### Design

By treating Shapez.io as a frontend, we hope to create a bridge using a REST \
API developed in flask for python, to connect with a TensorFlow Python Backend.

### Current Progress

Adapting Shapez.io as a front to communicate with a python backend through \
the use of a REST API in flask as a bridge.

### Project Timeline

TODO: Insert a simple timeline of our project changes.

## Project Setup

### Python Virtual Environments (.venv) & Requirements

Save your python package requirements for easy install:

> pip freeze > src_ai/\_requirements.txt

Load python packages for easy installation:

> pip install -r src_ai/\_requirements.txt

### Launching

Two terminals are required, one for the python backend and another for the
game frontend.

## File Structure

#### Project Configuration

> src_ai/\_readme.md -> Information on Project Development \
> src_ai/\_requirements.txt -> Python Package Tracking \
> src_ai/\_Shapez.AI.ipynb -> AI Model Visualisations

#### Frontend Entrypoint

> mod_examples/\_mod_ai_wrapper.js -> Game Interactions & Frontend Entrypoint

#### Python Backend Systems

> src_ai/app.py -> Backend Entrypoint \
> src_ai/model.py -> AI Model \
> src_ai/signals.py -> REST API

## New Features/Buttons include:
1. Shift + i: Gives information on how to use this mod.
2. Shift + t: Allows you to watch the model train.
3. Shift + r: Resets the game.
4. Shift + q: Allows you to see the best next move or moves as a blueprint. You can either choose to place the entity down with the left mouse click or disgard it with the right mouse click.

<hr>

<a href="" title="shapez.ai">
    <img src="src_ai/docs/poster.jpg" alt="shapezy">
</a>

<hr>
