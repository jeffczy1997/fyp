class Piece:
    def __init__(self):
        self.name = ["Elephant", "Lion", "Tiger", "Leopard", "Dog", "Wolf", "Cat", "Mouse"]
        self.rank = {self.name[0]: 8, self.name[1]: 7, self.name[2]: 6, self.name[3]: 5, self.name[4]: 4,
                     self.name[5]: 3, self.name[6]: 2, self.name[7]: 1}
        self.special = {self.name[1]: "Jump", self.name[2]: "Jump", self.name[7]: "Swim"}

    def myMoves(self, r, c, name):
        river = [[3, 1], [3, 2], [3, 4], [3, 5], [4, 1], [4, 2], [4, 4], [4, 5], [5, 1], [5, 2], [5, 4], [5, 5]]
        up = [r - 1, c]
        down = [r + 1, c]
        left = [r, c - 1]
        right = [r, c + 1]
        moves = []
        invalidMoves = []

        if not up[0] < 0:
            moves.append(up)
        if not down[0] > 8:
            moves.append(down)
        if not left[1] < 0:
            moves.append(left)
        if not right[1] > 6:
            moves.append(right)

        for i in range(len(moves)):
            if moves[i] in river:
                if name in self.special:
                    if self.special[name] == "Jump":
                        if up in river:
                            moves[moves.index(up)][0] -= 3
                        if down in river:
                            moves[moves.index(down)][0] += 3
                        if left in river:
                            moves[moves.index(left)][1] -= 2
                        if right in river:
                            moves[moves.index(right)][1] += 2
                else:
                    invalidMoves.append(moves[i])
        for move in invalidMoves:
            if move in moves:
                moves.remove(move)
        return moves
