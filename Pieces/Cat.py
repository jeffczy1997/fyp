from Pieces.Piece import Piece


class Cat(Piece):
    def __init__(self, player):
        self.name = "Cat"
        self.rank = 2
        self.player = player
        self.pos = self.myPos(12)
        self.power = self.specialPiece(self.name)
        self.moves = self.myMoves(self.pos)

