from Pieces.Piece import Piece


class Mouse(Piece):
    def __init__(self, player):
        self.name = "Mouse"
        self.rank = 1
        self.player = player
        self.pos = self.myPos(14)
        self.power = self.specialPiece(self.name)
        self.moves = self.myMoves(self.pos)
