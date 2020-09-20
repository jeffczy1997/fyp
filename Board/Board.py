from Board.Move import Move
from Pieces import Piece

class Board:
    def __init__(self):
        self.tiles = [["RLion", "-", "-", "F", "-", "-", "RTiger"],
                      ["-", "RDog", "-", "-", "-", "RCat", "-"],
                      ["RMouse", "-", "RLeopard", "-", "RWolf", "-", "RElephant"],
                      ["-", "-", "-", "-", "-", "-", "-"],
                      ["-", "-", "-", "-", "-", "-", "-"],
                      ["-", "-", "-", "-", "-", "-", "-"],
                      ["BElephant", "-", "BWolf", "-", "BLeopard", "-", "BMouse"],
                      ["-", "BCat", "-", "-", "-", "BDog", "-"],
                      ["BTiger", "-", "-", "F", "-", "-", "BLion"]]
        self.river = [[3, 1], [3, 2], [3, 4], [3, 5], [4, 1], [4, 2], [4, 4], [4, 5], [5, 1], [5, 2], [5, 4], [5, 5]]
        self.trap = {"R": [[0, 2], [0, 4], [1, 3]], "B": [[7, 3], [8, 2], [8, 4]]}
        self.den = [[0, 3], [8, 3]]
        self.jumps = [[2, 1], [2, 2], [2, 4], [2, 5], [6, 1], [6, 2], [6, 4], [6, 5], [3, 0], [4, 0], [5, 0], [3, 3],
                      [4, 3], [5, 3], [3, 6], [4, 6], [5, 6]]
        self.redToMove = True
        self.moveLog = []
        self.gameOver = False

    def state(self):
        return self.tiles

    def score(self):
        if self.checkGameOver():
            return 100
        highest_score = 0
        currentPieces = []
        for row in self.tiles:
            for cell in row:
                if not cell == "-":
                    currentPieces.append(cell)
        moved = self.moveLog[-1]
        self.undoMove()
        previousPiece = []
        for row in self.tiles:
            for cell in row:
                if not cell == "-":
                    previousPiece.append(cell)
        self.makeMove(moved)
        if len(previousPiece) > len(currentPieces):
            eaten = list(set(previousPiece).difference(set(currentPieces)))[0]
            if "Elephant" in eaten or "Lion" in eaten or "Tiger" in eaten or "Mouse" in eaten:
                highest_score = 10
            else:
                highest_score = 8
        piece = self.state()[moved.endRow][moved.endCol]
        if "Lion" in piece or "Tiger" in piece:
            player = piece[0]
            if player == "B":
                if True if moved.startRow > moved.endRow else False:
                    score = (8 - moved.endRow) / 8 * 1.01
                    if highest_score < score:
                        highest_score = score
        return highest_score

    def makeMove(self, move):
        self.tiles[move.startRow][move.startCol] = "-"
        self.tiles[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        self.redToMove = not self.redToMove

    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.tiles[move.startRow][move.startCol] = move.pieceMoved
            self.tiles[move.endRow][move.endCol] = move.pieceCaptured
            self.redToMove = not self.redToMove
        if self.checkGameOver():
            self.gameOver = False

    def getValidMoves(self):
        validMoves = []
        pieces = {"R": Piece.Piece(), "B": Piece.Piece()}
        for r in range(len(self.tiles)):
            for c in range(len(self.tiles[r])):
                turn = self.tiles[r][c][0]
                opponent = "A"
                if turn == "R":
                    opponent = "B"
                else:
                    opponent = "R"
                if (turn == "R" and self.redToMove) or (turn == "B" and not self.redToMove):
                    piece = self.tiles[r][c]
                    pieceName = self.getPieceName(piece)
                    moves = pieces[turn].myMoves(r, c, pieceName)
                    for move in moves:
                        jumpMove = False
                        if abs(move[0] - r) == 4 or abs(move[1] - c) == 3:
                            jumpMove = True
                        # Lion and Tiger Jumping moves
                        if (pieceName == "Lion" or pieceName == "Tiger") and jumpMove:
                            mouseBlock = False
                            mouseInRiver = False
                            mouseLocation = 0
                            if [r, c] in self.jumps and move in self.jumps:
                                for i in self.river:
                                    if not self.tiles[i[0]][i[1]] == "-":
                                        mouseInRiver = True
                                        mouseLocation = i
                                if mouseInRiver:
                                    if mouseLocation[1] == c:
                                        mouseBlock = True
                                    elif mouseLocation[0] == r:
                                        if abs(mouseLocation[1] - c) <= 2 and abs(move[1] - mouseLocation[1]) <= 2:
                                            mouseBlock = True
                            if not mouseBlock:
                                if self.tiles[move[0]][move[1]] == "-":
                                    validMoves.append(Move((r, c), move, self))
                                else:
                                    if not (self.tiles[move[0]][move[1]][0] == turn):
                                        if pieces[turn].rank[pieceName] >= pieces[opponent].rank[
                                            self.getPieceName(self.tiles[move[0]][move[1]])]:
                                            validMoves.append(Move((r, c), move, self))

                        elif self.tiles[move[0]][move[1]] == "-":
                            validMoves.append(Move((r, c), move, self))
                        elif self.tiles[move[0]][move[1]] == "F":
                            # Prevent Entering Self Den
                            if (not (turn == "R" and move == self.den[0])) and (
                                    not (turn == "B" and move == self.den[1])):
                                validMoves.append(Move((r, c), move, self))
                        else:
                            # Capturing or Teammate blocking
                            if self.tiles[move[0]][move[1]][0] == opponent:
                                # Mouse movements
                                if pieceName == "Mouse":
                                    mouseInRiver = False
                                    if [r, c] in self.river:
                                        mouseInRiver = True
                                    if (self.getPieceName(
                                            self.tiles[move[0]][move[1]]) == "Mouse" or self.getPieceName(self.tiles[move[0]][move[1]]) == "Elephant") and not mouseInRiver:
                                        validMoves.append(Move((r, c), move, self))
                                # Elephant movements
                                elif pieceName == "Elephant":
                                    if not (self.getPieceName(self.tiles[move[0]][move[1]]) == "Mouse"):
                                        validMoves.append(Move((r, c), move, self))
                                # Capturing
                                else:
                                    # Capturing piece in self trap
                                    if move in self.trap[turn]:
                                        pieces[opponent].rank[self.getPieceName(self.tiles[move[0]][move[1]])] = 0
                                    if pieces[turn].rank[pieceName] >= pieces[opponent].rank[
                                            self.getPieceName(self.tiles[move[0]][move[1]])]:
                                        validMoves.append(Move((r, c), move, self))
        return validMoves

    def getPieceName(self, piece):
        string = ""
        for i in range(len(piece)):
            if i > 0:
                string += piece[i]
        return string

    def checkGameOver(self):
        piecesCounter = {"R": 0, "B": 0}
        for r in range(len(self.tiles)):
            for c in range(len(self.tiles[r])):
                if not (self.tiles[r][c] == "-") and not(self.tiles[r][c] == "F"):
                    team = self.tiles[r][c][0]
                    piecesCounter[team] += 1
                for i in self.den:
                    if not self.tiles[i[0]][i[1]] == "F":
                        self.gameOver = True
        if piecesCounter["R"] == 0 or piecesCounter["B"] == 0:
            self.gameOver = True
        return self.gameOver
