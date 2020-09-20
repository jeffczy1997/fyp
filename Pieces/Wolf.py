from Pieces.Piece import Piece


class Wolf(Piece):
    def __init__(self, player):
        self.name = "Wolf"
        self.rank = 3
        self.player = player
        self.pos = self.myPos(18)
        self.power = self.specialPiece(self.name)
        self.moves = self.myMoves(self.pos)
