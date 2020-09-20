from Pieces.Piece import Piece


class Tiger(Piece):
    def __init__(self, player):
        self.name = "Tiger"
        self.rank = 6
        self.player = player
        self.pos = self.myPos(6)
        self.power = self.specialPiece(self.name)
        self.moves = self.myMoves(self.pos)
