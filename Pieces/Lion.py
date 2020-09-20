from Pieces.Piece import Piece


class Lion(Piece):
    def __init__(self, player):
        self.name = "Lion"
        self.rank = 7
        self.player = player
        self.pos = self.myPos(0)
        self.power = self.specialPiece(self.name)
        self.moves = self.myMoves(self.pos)
