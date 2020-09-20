import pickle
import numpy as np
from json import loads
from tensorflow.keras.callbacks import EarlyStopping

import pygame as p
from final_ai import AI
from Board import Board

p.init()
width = height = 800
dimensionW = 7
dimensionH = 9
sq_size = height // dimensionH
images = {}

# Initialization of images, will only called once
def loadImages():
    pieces = ["RElephant", "RLion", "RTiger", "RLeopard", "RDog", "RWolf", "RCat", "RMouse", "BElephant", "BLion",
              "BTiger", "BLeopard", "BDog", "BWolf", "BCat", "BMouse", "Trap", "River", "Grass", "RFlag", "BFlag"]
    for piece in pieces:
        images[piece] = p.transform.scale(p.image.load("Images/" + piece + ".jpeg"), (sq_size - 10, sq_size - 10))

def highlightSquares(screen, gs, validMoves, sqSelected):
    if not sqSelected == ():
        r, c = sqSelected
        if gs.tiles[r][c][0] == ("R" if gs.redToMove else "B"):
            s = p.Surface((sq_size, sq_size))
            # Transparency Value, 0 = Transparent ,Higher = less transparent
            s.set_alpha(300)
            s.fill(p.Color(255, 246, 4))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (sq_size * move.endCol, sq_size * move.endRow))


# Responsible for all graphics within current gamestate
def drawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen)
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.tiles)


def drawBoard(screen):
    for i in range(dimensionH):
        for j in range(dimensionW):
            p.draw.rect(screen, p.Color("white"), p.Rect(j * sq_size, i * sq_size, sq_size, sq_size))
            p.draw.rect(screen, p.Color("black"), p.Rect(j * sq_size, i * sq_size, sq_size, sq_size), 1)


def drawPieces(screen, board):
    river = [[3, 1], [3, 2], [3, 4], [3, 5], [4, 1], [4, 2], [4, 4], [4, 5], [5, 1], [5, 2], [5, 4], [5, 5]]
    trap = [[0, 2], [0, 4], [1, 3], [7, 3], [8, 2], [8, 4]]
    den = [[0, 3], [8, 3]]
    for i in range(dimensionH):
        for j in range(dimensionW):
            piece = board[i][j]
            arr = [i, j]
            if not piece == "-" and not piece == "F":
                screen.blit(images[piece], p.Rect(j * sq_size + 5, i * sq_size + 5, sq_size - 10, sq_size - 10))
            elif arr in river:
                screen.blit(images["River"], p.Rect(j * sq_size + 5, i * sq_size + 5, sq_size - 10, sq_size - 10))
            elif arr in trap:
                screen.blit(images["Trap"], p.Rect(j * sq_size + 5, i * sq_size + 5, sq_size - 10, sq_size - 10))
            elif arr == den[0]:
                screen.blit(images["RFlag"], p.Rect(j * sq_size + 5, i * sq_size + 5, sq_size - 10, sq_size - 10))
            elif arr == den[1]:
                screen.blit(images["BFlag"], p.Rect(j * sq_size + 5, i * sq_size + 5, sq_size - 10, sq_size - 10))
            else:
                screen.blit(images["Grass"], p.Rect(j * sq_size + 5, i * sq_size + 5, sq_size - 10, sq_size - 10))


def drawText(screen, text):
    font = p.font.SysFont("Melvitca", 32, True, False)
    textObject = font.render(text, 0, p.Color("Black"))
    textLocation = p.Rect(0, 0, width, height).move(width / 2 - textObject.get_width() / 2,
                                                    height / 2 - textObject.get_height() / 2)
    screen.blit(textObject, textLocation)

def main_train():
    while True:
        ai = AI("Best.h5")
        game = Board.Board()
        ai.simulate(game)
        # data = pickle.loads(open("data.pkl", "rb+").read())
        states = []
        actions = []
        scores = []
        for state_json in ai.scores.keys():
            state = loads(state_json)
            states += [state]
            scores += [ai.scores[state_json]]
        file = open("data.pkl", "wb+")
        data_str = pickle.dumps(ai.scores, pickle.HIGHEST_PROTOCOL)
        file.write(data_str)
        file.close()
        ai.model.fit(
            x=(
                np.array(
                    [
                        np.array([a for a in map(lambda x: np.array(
                            [z for z in map(lambda y: hash(y), x)]
                        ), state)]) for state in states
                    ]
                )
                .astype(float).reshape(-1, 9, 7, 1)
            ),
            y=np.array(scores),
            batch_size=1,
            epochs=100,
            verbose=True,
            validation_split=0.3,
            callbacks=[EarlyStopping(patience=3)]
        )
        ai.model.save("Current.h5")
        p.init()
        score = [0, 0]
        screen = p.display.set_mode((width, height))
        screen.fill(p.Color("white"))
        for _ in range(0, 10):
            ai1 = AI("Best.h5")
            ai2 = AI("Current.h5")
            gs = Board.Board()
            loadImages()
            repeat = 0
            while True:
                if (score[0] > 4 + score[1]) or (score[1] > 4 + score[0]):
                    break
                if len(gs.moveLog) >= 6 and ((gs.moveLog[-1].getPieceNotation() == gs.moveLog[-5].getPieceNotation()) and (gs.moveLog[-2].getPieceNotation() == gs.moveLog[-6].getPieceNotation())):
                    repeat += 1
                else:
                    repeat = 0
                if repeat == 3:
                    break
                p.event.get()
                move = ai1.ai_move(gs)
                gs.makeMove(move)
                p.display.update()
                drawGameState(screen, gs, gs.getValidMoves(), ())
                if gs.checkGameOver():
                    if gs.redToMove:
                        score[0] += 1
                        drawText(screen, "Blue Wins!")
                    else:
                        score[1] += 1
                        drawText(screen, "Red Wins!")
                    break
                else:
                    p.event.get()
                    move2 = ai2.ai_move(gs)
                    gs.makeMove(move2)
                    p.display.update()
                    drawGameState(screen, gs, gs.getValidMoves(), ())
                if gs.checkGameOver():
                    if gs.redToMove:
                        score[0] += 1
                        drawText(screen, "Blue Wins!")
                    else:
                        score[1] += 1
                        drawText(screen, "Red Wins!")
                    break
            red_pieces = []
            blue_pieces = []
            for row in gs.state():
                for cell in row:
                    if cell[0] == "R":
                        red_pieces += [cell]
                    elif cell[0] == "B":
                        blue_pieces += [cell]
            if len(blue_pieces) > len(red_pieces):
                score[0] += 1
            elif len(red_pieces) > len(blue_pieces):
                score[1] += 1
            print(f"Blue: {score[0]} Red: {score[1]}")
        if score[0] > 4 + score[1]:
            ai2.model.save("Best.h5")
        else:
            ai1.model.save("Best.h5")

main_train()