import gym
import numpy as np

import config
import turtles_logic

from stable_baselines import logger

class TurtlesEnv(gym.Env):
  metadata = {'render.modes': ['human']}

  def __init__(self, verbose = False, manual = False):
    super(TurtlesEnv, self).__init__()

    self.logic = TurtlesLogic()

    self.name = 'turtles'
    self.manual = manual

    self.n_players = 2
    self.action_space = gym.spaces.Discrete(self.logic.move_length())
    self.observation_space = gym.spaces.Box(0, 1, (19,))
    self.verbose = verbose

  @property
  def observation(self):
    # 1 bit for whether player still has a move left
    # 18 bits for each turtle, determining its position = 18*18 = 324
    # could also try 1 bit for each turtle, position as -1 - 1 (e.g. 0.5)
    return np.array([
      [1 if self.logic.actions == 2 else 0],
      self.logic.turtle_pos[0][1:],
      self.logic.turtle_pos[1][1:],
    ]).flatten()

  @property
  def legal_actions(self):
    return np.array(self.logic.legal_moves())

  def step(self, action):
    self.logic.step(action)
    reward = [0, 0]
    done = False
    if self.logic.scores[0] >= 7:
      reward = [1, 0]
      done = True
    elif self.logic.scores[1] >= 7:
      reward = [0, 1]
      done = True
    return self.observation, reward, done, {}

  def reset(self):
    self.logic.reset()
    return self.observation

  def render(self, mode='human', close=False, verbose = True):
    self.logic.print()
