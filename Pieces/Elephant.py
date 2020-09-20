from Pieces.Piece import Piece


class Elephant(Piece):
    def __init__(self, player):
        self.name = "Elephant"
        self.rank = 8
        self.player = player
        self.pos = self.myPos(20)
        self.power = self.specialPiece(self.name)
        self.moves = self.myMoves(self.pos)



