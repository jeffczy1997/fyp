from Pieces.Piece import Piece


class Leopard(Piece):
    def __init__(self, player):
        self.name = "Leopard"
        self.rank = 5
        self.player = player
        self.pos = self.myPos(16)
        self.power = self.specialPiece(self.name)
        self.moves = self.myMoves(self.pos)
