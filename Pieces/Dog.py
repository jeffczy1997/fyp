from Pieces.Piece import Piece


class Dog(Piece):
    def __init__(self, player):
        self.name = "Dog"
        self.rank = 4
        self.player = player
        self.pos = self.myPos(8)
        self.power = self.specialPiece(self.name)
        self.moves = self.myMoves(self.pos)
