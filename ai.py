import random
import math
import threading
import pickle
import signal
import sys
import numpy as np
from json import dumps, loads
from agent import create_model
from tensorflow.keras.models import load_model

class TicTacToe:
	def __init__(self):
		self.moves = []

	def __str__(self):
		player_one = [move for i, move in enumerate(self.moves) if i % 2 == 0]
		player_two = [move for i, move in enumerate(self.moves) if i % 2 == 1]

		row_string = "-------\n"
		for y in range(0,3):
			row_string += "|"
			for x in range(0,3):
				pos = y * 3 + x
				if pos in player_one:
					row_string += "O"
				elif pos in player_two:
					row_string += "X"
				else:
					row_string += " "
				row_string += "|"
			row_string += "\n-------\n"
		return row_string

	def state(self):
		player_one = [move for i, move in enumerate(self.moves) if i % 2 == 0]
		player_two = [move for i, move in enumerate(self.moves) if i % 2 == 1]
		return ["O" if i in player_one else ("X" if i in player_two else None) for i in range(0,9)]

	def undo(self):
		self.moves.pop()

	def move(self, move):
		if move in self.moves:
			return False
		else:
			self.moves += [move]
			return True

	def over(self):
		return self.check_win() or len(self.moves) == 9

	def score(self):
		return self.check_win()

	def valid_moves(self):
		return list(set({0,1,2,3,4,5,6,7,8}).difference(set(self.moves)))

	def check_win(self):
		win_conds = [
			[0,1,2],
			[3,4,5],
			[6,7,8],
			[0,3,6],
			[1,4,7],
			[2,5,8],
			[0,4,8],
			[2,4,6]
		]
		player_one = [move for i, move in enumerate(self.moves) if i % 2 == 0]
		player_two = [move for i, move in enumerate(self.moves) if i % 2 == 1]

		for win_cond in win_conds:
			if len(set(player_one).intersection(set(win_cond))) == 3 or len(set(player_two).intersection(set(win_cond))) == 3:
				return 1
		return 0

class AI_ALGO():
	def simulate(self, game, step=8):
		if step == 0 or game.score():
			return game.score()
		move = random.choice(game.getValidMoves())
		game.makeMove(move)
		score = -self.simulate(game, step - 1)
		game.undoMove()
		return score

	def replay_score(self, game, N=300):
		scores = [self.simulate(game) for i in range(0, N)]
		return sum(scores) / len(scores)

	def ai_move(self, game):
		actions = {}
		for move in game.getValidMoves():
			game.makeMove(move)
			actions[move.moveID] = self.replay_score(game)
			game.undoMove()
		move_id = max(actions, key=actions.get)
		return next(action for action in game.getValidMoves() if action.moveID == move_id)

class AI_UCT():
	def __init__(self):
		self.visits = {}
		self.differential = {}

	def heusomething_value(self, game):
		N = self.visits.get("total", 1)
		Ni = self.visits.get(str(game.state()), 1e-5)
		V = self.differential.get(str(game.state()), 0) * 1.0 / Ni
		return V + 1.5 * math.sqrt(math.log(N) / Ni)

	def record(self, game, score):
		self.visits["total"] = self.visits.get("total", 1) + 1
		self.visits[str(game.state())] = self.visits.get(str(game.state()), 0) + 1
		self.differential[str(game.state())] = self.differential.get(str(game.state()), 0) + score

	def simulate(self, game, steps=7):
		if steps == 0 or game.checkGameOver():
			return -game.score()

		action_heusomething = {}
		for move in game.getValidMoves():
			game.makeMove(move)
			action_heusomething[move.moveID] = self.heusomething_value(game)
			game.undoMove()

		move_id = max(action_heusomething, key=action_heusomething.get)
		move = next(action for action in game.getValidMoves() if action.moveID == move_id)
		game.makeMove(move)
		score = -self.simulate(game, steps - 1)
		game.undoMove()
		self.record(game, score)

		return score

	def replay_score(self, game, N=100):
		for i in range(0, N):
			self.simulate(game)
		return self.differential[str(game.state())] * 1.0 / self.visits[str(game.state())]

	def ai_move(self, game):
		actions = {}
		for move in game.getValidMoves():
			game.makeMove(move)
			if game.checkGameOver():
				actions[move.moveID] = math.inf
			else:
				actions[move.moveID] = -self.replay_score(game)
			game.undoMove()
		move_id = max(actions, key=actions.get)
		return next(action for action in game.getValidMoves() if action.moveID == move_id)

class AI():
	def __init__(self, name):
		self.name = name
		self.visits = {}
		self.scores = {}
		try:
			self.model = load_model(self.name)
		except OSError:
			self.model = create_model()

	def explore(self, game):
		score = self.model.predict(
			(
				np.expand_dims(
					np.array(list(map(lambda x: np.array(list(map(lambda y: hash(y), x))),
					game.state()))).reshape((9, 7, 1)).astype(float), axis=0
				),
				np.array([game.moveLog[-1].moveID]).reshape((1, 1, 1))
			)
		)[0][0]
		self.visits[dumps(game.state())] = self.visits.get(dumps(game.state()), 0) + 1
		return -score

	def rollout(self, game, acc, steps=50):
		if steps == 0 or game.checkGameOver():
			print("Reached terminal node, backtracking...")
			return -acc

		if self.visits.get(dumps(game.state())) == None:
			print("Reached unknown move, exploring using nn...")
			return self.explore(game)

		print(f"Move {game.moveLog[-1].getPieceNotation()} was previously made.")
		best_action = []
		best_score = -float("inf")

		print("Choosing best move to rollout...")
		for move in game.getValidMoves():
			parent_state_visits = self.visits.get(dumps(game.state()))
			game.makeMove(move)
			Q = self.scores.get(dumps(game.state()))
			if not Q:
				score = self.explore(game)
				Q = score
			score = Q + 1.5 * math.sqrt(parent_state_visits / self.visits[dumps(game.state())])
			print(f"Score for {move.getPieceNotation()} is {score}")
			game.undoMove()
			if score > best_score:
				best_score = score
				best_action = [move]
			elif score == best_score:
				best_action += [move]

		try:
			best_action = random.choice(best_action)
		except:
			breakpoint()
		print("Chosen best move to rollout, continue rolling...")
		game.makeMove(best_action)
		try:
			score = self.rollout(game, -(acc + game.score()), steps - 1)
		except RecursionError:
			score = acc + game.score()
		game.undoMove()
		print("Rollout completed for current node, fine tuning score.")
		self.visits[dumps(game.state())] = self.visits.get(dumps(game.state()), 0) + 1
		self.scores[dumps(game.state())] = (self.scores.get(dumps(game.state()), 0) + score) / self.visits[dumps(game.state())]
		return -score


	def simulate(self, game):
		while not game.checkGameOver() and len(game.moveLog) < 50:
			best_m = []
			best_s = -float("inf")
			for move in game.getValidMoves():
				print(f"Simulating from leaf move {move.getPieceNotation()}.")
				game.makeMove(move)
				score = self.rollout(game, -game.score())
				print(f"Updating score for {move.getPieceNotation()}...")
				self.visits[dumps(game.state())] = self.visits.get(dumps(game.state()), 0) + 1
				self.scores[dumps(game.state())] = (self.scores.get(dumps(game.state()), 0) + score) / self.visits[dumps(game.state())]
				if self.scores[dumps(game.state())] >= best_s:
					best_m += [move]
					best_s = self.scores[dumps(game.state())]
				game.undoMove()
			game.makeMove(random.choice(best_m))

	def ai_move(self, game):
		best_score = -float("inf")
		best_move = []
		for move in game.getValidMoves():
			game.makeMove(move)
			score = self.model.predict(
				(
					np.expand_dims(
						np.array(list(map(lambda x: np.array(list(map(lambda y: hash(y), x))),
						game.state()))).reshape((9, 7, 1)).astype(float), axis=0
					)
				)
			)[0][0]
			if score > best_score:
				best_score = score
				best_move = [move]
			elif score == best_score:
				best_move += [move]
			game.undoMove()
		best_move = random.choice(best_move)
		print(f"Picking {best_move.getPieceNotation()} of score: {best_score}")
		return best_move
			
	# def heusomething_value(self, game):
	# 	N = self.visits.get("total", 1)
	# 	Ni = self.visits.get(str(game.state()), 1e-5)
	# 	V = self.differential.get(str(game.state()), 0) * 1.0 / Ni
	# 	return V + 1.5 * math.sqrt(math.log(N) / Ni)
	# 	# return self.model.predict(np.expand_dims(np.array(list(map(lambda x: np.array(list(map(lambda y: hash(y), x))), game.state()))).reshape((9, 7, 1)).astype(float), axis=0))[0][0]

	# def record(self, game, score):
	# 	self.model.fit(x=np.array([a for a in map(lambda x: np.array([z for z in map(lambda y: hash(y), x)]), game.state())]).astype(float).reshape(-1, 9, 7, 1), y=np.array([score]), batch_size=1, verbose=True)

	# def simulate(self, game, steps=7):
	# 	if steps == 0 or game.checkGameOver():
	# 		return -game.score()

	# 	action_heusomething = {}
	# 	for move in game.getValidMoves():
	# 		game.makeMove(move)
	# 		action_heusomething[move.moveID] = self.heusomething_value(game)
	# 		game.undoMove()

	# 	move_id = max(action_heusomething, key=action_heusomething.get)
	# 	move = next(action for action in game.getValidMoves() if action.moveID == move_id)
	# 	game.makeMove(move)
	# 	score = -self.simulate(game, steps - 1)
	# 	game.undoMove()
	# 	self.record(game, score)

	# 	return score

	# def replay_score(self, game, N=1):
	# 	scores = [self.simulate(game) for _ in range(0, N)]
	# 	score = sum(scores) / len(scores)
	# 	return score

	# def ai_move(self, game):
	# 	actions = {}
	# 	for move in game.getValidMoves():
	# 		game.makeMove(move)
	# 		if game.checkGameOver():
	# 			actions[move.moveID] = math.inf
	# 		else:
	# 			actions[move.moveID] = -self.replay_score(game)
	# 		game.undoMove()
	# 	move_id = max(actions, key=actions.get)
	# 	self.model.save(self.name)
	# 	return next(action for action in game.getValidMoves() if action.moveID == move_id)

if __name__ == "__main__":

	wins = {"one": 0, "two": 0}

	ai2 = AI_UCT()
	try:
		file = open("agent.pkl", "rb+")
		ai1 = pickle.load(file)
		ai2.visits = ai1.visits
		ai2.differential = ai1.differential
	except FileNotFoundError:
		ai1 = AI_UCT()
	
# 	def stop(sig, frame):
# 		print("Saving agent...")
# 		file = open("agent.pkl", "wb+")
# 		pickle.dump(ai2, file, pickle.HIGHEST_PROTOCOL)
# 		sys.exit(0)

# 	signal.signal(signal.SIGINT, stop)

# 	def one_game(first, second):
# 		for i in range(0, 1000):
# 			game = TicTacToe()
# 			while not game.over():
# 				print(game)
# 				move = first.ai_move(game)
# 				# move = random.choice(game.valid_moves())
# 				if game.move(move) and not game.over():
# 					move2 = second.ai_move(game)
# 					game.move(move2)
# 			if game.score() > 0:
# 				if len(game.moves) % 2 == 0:
# 					wins["two"] += 1
# 				else:
# 					wins["one"] += 1
# 			print(f"""
# {game}\n
# Player one: {wins['one']}
# Player two: {wins['two']}
# 		""")
	
# 	while True:
# 		one_game(ai1, ai2)
# 		one_game(ai2, ai1)

	# threads = []

	# for i in range(0, 100):
	# 	first = ai1 if i % 2 == 0 else ai2
	# 	second = ai2 if i % 2 == 0 else ai1
	# 	t = threading.Thread(target=one_game,args=(first, second))
	# 	threads += [t]
	# 	t.start()

	# print("Started all threads, joining...")

	# for t in threads:
	# 	t.join()

	while True:
		game = TicTacToe()
		while not game.over():
			print(game)
			move = int(input("Give number: "))
			if game.move(move) and not game.over():
				move2 = ai2.ai_move(game)
				game.move(move2)
		print(game)
		# breakpoint()

	# hash(frozenset({"asd": "qwe"}.items()))

