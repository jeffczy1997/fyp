import random
import math
import numpy as np
from json import dumps
from agent import create_model
from tensorflow.keras.models import load_model

class AI():

    def rollout(self, game, acc, steps=3):
        if steps == 0 or game.checkGameOver():
            return acc
        best_m = []
        best_s = -float("inf")
        for move in game.getValidMoves():
            game.makeMove(move)
            score = self.rollout(game, -(acc + game.score()), steps - 1)
            if score > best_s:
                best_m = [move]
                best_s = score
            elif score == best_s:
                best_m += [move]
            game.undoMove()
        return -score

    def ai_move(self, game):
        best_m = []
        best_s = -float("inf")
        for move in game.getValidMoves():
            game.makeMove(move)
            score = self.rollout(game, -game.score())
            game.undoMove()
            if score > best_s:
                best_m = [move]
                best_s = score
            elif score == best_s:
                best_m += [move]
        return random.choice(best_m)

    # def __init__(self, name):
    #     self.name = name
    #     self.scores = {}
    #     try:
    #         self.model = load_model(self.name)
    #     except OSError:
    #         self.model = create_model()

    # def record(self, game, score):
    #     self.scores[dumps(game.state())] = (self.scores.get(dumps(game.state()), 0) + score) / 2

    # def rollout(self, game, acc, steps=15):
    #     if steps == 0 or game.checkGameOver():
    #         return -acc
    #     best_m = []
    #     best_s = -float("inf")
    #     for move in game.getValidMoves():
    #         score = self.model.predict(
    #             (
    #                 np.expand_dims(
    #                     np.array(list(map(lambda x: np.array(list(map(lambda y: hash(y), x))),
    #                     game.state()))).reshape((9, 7, 1)).astype(float), axis=0
    #                 )
    #             )
    #         )[0][0]
    #         if score > best_s:
    #             best_m = [move]
    #             best_s = score
    #         elif score == best_s:
    #             best_m += [move]
    #     game.makeMove(move)
    #     score = self.rollout(game, -(acc + game.score()), steps - 1)
    #     self.record(game, score)
    #     game.undoMove()
    #     return -score

    # def simulate(self, game):
    #     while not game.checkGameOver() and len(game.moveLog) < 50:
    #         print(f"Simulating move {len(game.moveLog) + 1}")
    #         best_m = []
    #         best_s = -float("inf")
    #         for move in game.getValidMoves():
    #             game.makeMove(move)
    #             score = self.rollout(game, -game.score())
    #             if score > best_s:
    #                 best_m = [move]
    #                 best_s = score
    #             elif score == best_s:
    #                 best_m += [move]
    #             self.record(game, score)
    #             game.undoMove()
    #         game.makeMove(random.choice(best_m))

    # def ai_move(self, game):
    #     best_score = -float("inf")
    #     best_move = []
    #     for move in game.getValidMoves():
    #         game.makeMove(move)
    #         score = self.model.predict(
    #             (
    #                 np.expand_dims(
    #                     np.array(list(map(lambda x: np.array(list(map(lambda y: hash(y), x))),
    #                     game.state()))).reshape((9, 7, 1)).astype(float), axis=0
    #                 )
    #             )
    #         )[0][0]
    #         if score > best_score:
    #             best_score = score
    #             best_move = [move]
    #         elif score == best_score:
    #             best_move += [move]
    #         game.undoMove()
    #     best_move = random.choice(best_move)
    #     print(f"Picking {best_move.getPieceNotation()} of score: {best_score}")
    #     return best_move