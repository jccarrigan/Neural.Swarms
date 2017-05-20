#! /usr/bin/env python

# game imports
from random import random, sample, randint
from game import BoardGame
from board import Board
from figure import Figure, FigureStrategy
from logger import log

# utilities
import numpy as np

# Navigator game main class
class NaviGame(BoardGame):
    def __init__(self, height, width, goal = (0, 0), model=None):
        self.board = Board(height, width)
        self.goal = goal
        self.model = model

    def setup(self):
        self.Flag = Figure(self.board)
        self.Flag.bindStrategy(FlagStrategy())
        self.Flag.strategy.placeIt(self.goal[0], self.goal[1])
        self.Flag.color = 2
        self.Navigator = Figure(self.board)
        self.Navigator.bindStrategy(NaviStrategy(self.model, self.goal))
        self.Navigator.strategy.placeIt()
        self.Navigator.color = 1

    def shift_goal(self, goal = None):
        if goal == None:
            goal = (randint(0, self.board.height-1), randint(0, self.board.width-1))
        try:
            self.goal = goal
            self.Flag.move(y=goal[0], x=goal[1], relative=False)
            self.Navigator.strategy.goal = goal
        except:
            self.shift_goal()

# flag for the target location
class FlagStrategy(FigureStrategy):
    symbol = "~"

    def placeIt(self, x=None, y=None):
        if x == None and y == None:
            x = sample(range(0, self.board.width), 1)[0]
            y = sample(range(0, self.board.height), 1)[0]
        try:
            self.figure.add(y, x)
        except:
            self.placeIt(x=x+randint(0, 1), y=y+randint(0, 1))

    def step(self):
        pass

# navigator to get to target
class NaviStrategy(FigureStrategy):
    def __init__(self, model, goal):
        self.symbol = "."
        self.model = model
        self.goal = goal
        # stay, right, left, up, down (y, x)
        self.actions = [(0, 0), (0, 1), (0, -1), (1, 0), (-1, 0)]

    def placeIt(self):
        x = sample(range(0, self.board.width), 1)[0]
        y = sample(range(0, self.board.height), 1)[0]
        try:
            self.figure.add(y, x)
        except:
            self.placeIt()

    def get_input(self):
        ipt = list(self.figure.position())
        ipt.extend(list(self.goal))
        return ipt

    def plan_movement(self):
        ipt = self.get_input()
        dist_y = ipt[0] - ipt[2]
        dist_x = ipt[1] - ipt[3]
        if (dist_y == 1 and dist_x ==0) or (dist_y == 0 and dist_x == 1):
            # chill
            choice = 0
        else:
            # do something
            if abs(dist_y) < abs(dist_x):
                # x distance is greater
                if dist_x < 0:
                    # less than 0, so move right
                    choice = 1
                else:
                    choice = 2
            else:
                # y distance is greater or equal
                if dist_y < 0:
                    # less than 0, so move up
                    choice = 3
                else:
                    choice = 4
        return choice

    def step(self):
        ipt = self.get_input()
        if self.model != None:
            choice = self.model.predict(np.array(ipt).reshape(1, 4))
            action = self.actions[np.argmax(choice)]
        else:
            choice = self.plan_movement()
            action = self.actions[choice]
        try:
            self.figure.move(action[0], action[1], relative = True)
        except self.board.AboveWidthException:
            action = self.actions[0]
            #self.figure.move(action[0], action[1], relative = True)
        except self.board.AboveHeightException:
            action = self.actions[0]
            #self.figure.move(action[0], action[1], relative = True)
        except self.board.BelowWidthException:
            action = self.actions[0]
            #self.figure.move(action[0], action[1], relative = True)
        except self.board.BelowHeightException:
            action = self.actions[0]
            ##self.figure.move(action[0], action[1], relative = True)
        except self.board.TakenException:
            action = self.actions[0]

if __name__=='__main__':
    np.random.seed(2)
    random.seed(2)

    test_game = NaviGame(8, 8)
    test_game.setup()
