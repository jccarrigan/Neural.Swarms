# utilities
import pandas as pd
import numpy as np
import pylab as pl
import pickle
import os
from collections import Counter
# from tqdm import *

# import the game
from neural_navi_game import *
from notebook_game_helper import *

# imports for neural net
from keras.utils import np_utils
from keras.models import Sequential
from keras.layers.core import Dense
from keras.optimizers import sgd, RMSprop, Adagrad
import theano

def model_benchmark(model, actions, goal):
    print('''Prediction Test: If network does not provide differentiated
     responses to these inputs, keep training or modify network. The piece
    is on opposite sides of the goal here so the predicted rewards should
    be opposites.''')
    print(" Note that these outputs correspond to these actions:")
    print(" (y,x): ",actions)
    ipt0 = [goal[0], goal[1]+2]
    ipt0.extend(list(goal))
    predict0 = model.predict(np.array(ipt0).reshape(1,4))
    choice0 = np.argmax(predict0)
    # print(predict0, choice0)
    print('''   Position +(0, 1),  Goal {}: {}'''.format(goal, choice0))
    ipt1 = [goal[0], goal[1]-2]
    ipt1.extend(list(goal))
    predict1 = model.predict(np.array(np.array(ipt1)).reshape(1,4))
    choice1 = np.argmax(predict1)
    # print(predict1, choice1)
    print('''   Position -(0, 2), Goal {}: {}'''.format(goal, choice1))
    ipt2 = [goal[0]+2, goal[1]]
    ipt2.extend(list(goal))
    predict2 = model.predict(np.array(ipt2).reshape(1,4))
    choice2 = np.argmax(predict2)
    # print(predict2, choice2)
    print('''   Position +(2, 0),  Goal {}: {}'''.format(goal, choice2))
    ipt3 = [goal[0]-2, goal[1]]
    ipt3.extend(list(goal))
    predict3 = model.predict(np.array(ipt3).reshape(1,4))
    choice3 = np.argmax(predict3)
    # print(predict3, choice3)
    print('''   Position -(2, 0), Goal {}: {}'''.format(goal, choice3))
    # print(''' Are they equal? If so this is extra bad... ''')
    # print(model.predict(np.array([1,7]).reshape(1,2)) == model.predict(np.array([14,7]).reshape(1,2)))

# in: 4, out: 5
def baseline_model(optimizer = sgd(lr = 0.001),
                    layers = [{"size":20,"activation":"relu"}]):
    # one action for each direction and one for hold
    num_actions = 5
    # prepare the navigator model
    model = Sequential()
    # initial inputs
    l = list(layers)
    l0 = l[0]
    del l[0]
    model.add(Dense(l0['size'],
                    input_dim = 4,
                    activation = l0['activation']))
    # the hidden layers
    for layer in l:
        model.add(Dense(layer['size'], activation=layer['activation']))
    # the output layer
    model.add(Dense(num_actions, activation='sigmoid'))
    model.compile(optimizer = optimizer,
                    loss = "mean_squared_error")
    return model

# generate data for training the navigator
def train_data(game, figure, n = 100):
    inputs, targets = [], []
    last_choice = None
    for i in range(n):
        inputs.append(figure.strategy.get_input())
        choice = figure.strategy.plan_movement()
        t = [0, 0, 0, 0, 0]
        t[choice] = 1
        targets.append(t)
        if (choice == 0) and (last_choice == 0):
            break
        else:
            last_choice = choice
        game.step()
    # return the data
    return inputs, targets

def train_model(navi_game, model, steps = 1000,
                epochs = 20, batch_size = 32, verbose = 0,
                all_data = False, inputs = None, targets = None):
    if (inputs == None) and (targets == None):
        s = 0
        inputs, targets = [], []
        while s < steps:
            navi_game.shift_goal()
            inputsk, targetsk = train_data(navi_game, navi_game.Navigator, 10)
            inputs.extend(inputsk)
            targets.extend(targetsk)
            s += len(inputsk)
        print("Data generated, now fitting network")
    else:
        games = None
    log = model.fit(inputs, targets,
        verbose = verbose,
        epochs = epochs,
        batch_size = batch_size,
        shuffle=True)
    if all_data == True:
        return log, inputs, targets
    else:
        return log

if __name__=='__main__':
    # game variables
    epochs = 10
    batch_size = 10
    learning_rate = 0.05
    steps = 100
    training_game_size = 8

    # layers
    layers = [{"size":5,"activation":"tanh"},
                {"size":5,"activation":"tanh"}]

    # number of epochs for training
    epochs = epochs
    batch_size = batch_size

    # learning rate
    learning_rate = learning_rate

    # number of steps to take
    steps = steps

    # optimizer
    optimizer = sgd(lr=learning_rate)
    optimizer_str = "SGD(lr = "+str(learning_rate)+")"
    # make the model
    model = baseline_model(optimizer, layers)

    # prepare the game for collecting data
    # this has no model, so it uses the "perfect" strategy defined within
    test_game = NaviGame(training_game_size,
                        training_game_size,
                        moving_target = True)
    test_game.setup()

    print("Generating training data")
    # collect all data to make pickled runs!
    # stop regenerating the damn data!
    log, inputs, targets = train_model(
                navi_game = test_game,
                model = model,
                steps = steps,
                epochs = epochs,
                batch_size = batch_size,
                verbose = 1,
                all_data = True)
    # pull data points of for validation
    print("Network and final validation data ready for testing.")
        # prepare the game for final validation