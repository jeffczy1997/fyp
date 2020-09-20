import pygame as p
from ai import AI_ALGO
from Board import Board
from Board.Move import Move

p.init()
width = height = 800
dimensionW = 7
dimensionH = 9
sq_size = height // dimensionH
images = {}

def main():
    p.init()
    ai = AI_ALGO()
    screen = p.display.set_mode((width, height))
    screen.fill(p.Color("white"))
    gs = Board.Board()
    validMoves = gs.getValidMoves()
    moveMade = False
    loadImages()
    running = True
    squareSelected = ()
    playerClicks = []
    gameOver = False
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            # Mouse Actions
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver:
                    location = p.mouse.get_pos()
                    if location[0] <= sq_size * 7 and location[1] <= sq_size * 9:
                        col = location[0] // sq_size
                        row = location[1] // sq_size
                        if squareSelected == (row, col):
                            squareSelected = ()
                            playerClicks = []
                        else:
                            squareSelected = (row, col)
                            playerClicks.append(squareSelected)
                        if len(playerClicks) == 2:
                            move = Move(playerClicks[0], playerClicks[1], gs)
                            if move in validMoves:
                                gs.makeMove(move)
                                moveMade = True
                                if not gs.checkGameOver():
                                    gs.makeMove(ai.ai_move(gs))
                            squareSelected = ()
                            playerClicks = []
            # Keyboard Actions
            elif e.type == p.KEYDOWN:
                # Z key is Undo
                if e.key == p.K_z:
                    gs.undoMove()
                    moveMade = True
                # R key is Restart
                if e.key == p.K_r:
                    gs = Board.Board()
                    validMoves = gs.getValidMoves()
                    squareSelected = ()
                    playerClicks = []
                    moveMade = False

        if moveMade:
            validMoves = gs.getValidMoves()
            moveMade = False
        p.display.update()
        drawGameState(screen, gs, validMoves, squareSelected)

        if gs.checkGameOver():
            gameOver = True
            if gs.redToMove:
                drawText(screen, "Blue Wins!")
            else:
                drawText(screen, "Red Wins!")

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

main()