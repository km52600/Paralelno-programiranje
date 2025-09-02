import numpy as np
import itertools
import sys
import time
import numpy as np
import os

class Game:
    CPU = 1
    HUMAN = 2

    def __init__(self, rows=6, cols=7):
        self._rows = rows
        self._cols = cols
        self._board = [[0] * rows for _ in range(cols)]
        self._counter = {i: rows - 1 for i in range(cols)}

    @property
    def cols(self):
        return self._cols

    @property
    def rows(self):
        return self._rows


    def move(self, col, player):
        if not self.move_legal(col):
            return 0

        row = self._counter[col - 1]
        self._counter[col - 1] -= 1
        self._board[col - 1][row] = player

    def print_board(self):
        sys.stdout.flush()
        print("".join(["-" for i in range(30)]))
        for row in range(self._rows):
            print("| ", end="")
            for col in range(self._cols):
                if self._board[col][row] == self.HUMAN:
                    print("H", end=" | ")
                elif self._board[col][row] == self.CPU:
                    print("C", end=" | ")
                else:
                    print(" ", end=" | ")
            print()
            print("".join(["-" for i in range(30)]))
        print()

    def undo_move(self, col):
        # ako trebamo vratiti potez
        if self._counter[col - 1] == self._rows - 1 or col > self._cols:
            return 0

        row = self._counter[col - 1] + 1
        self._counter[col - 1] += 1
        self._board[col - 1][row] = 0

    def move_legal(self, col):
    # je li legalan potez
        if  col < 1 or self._counter.get(col - 1, -1) == -1 or col > self._cols:
            return 0
        else:
            return 1


    def game_end(self, col):
        if col > self._cols:
            return 0
        rows = self.rows
        cols = self.cols
        col = col - 1

        row = self._counter[col]
        row = row if row >= 5 else row + 1
        board = self._board
        player = self._board[col][row]

        # vertikalno
        seq = board[col][row:]
        if seq[:4].count(seq[0]) == 4 and len(seq) >= 4:
            return 1

        # horizontalno
        board = np.array(board).T.tolist()
        seq = board[row][:]
        broj = 0
        pom = col
        while board[row][pom - 1] == player and (pom - 1) >= 0:
            pom = pom - 1
        if len(seq[pom:]) >= 4:
            while pom < cols and board[row][pom] == player:
                broj = broj + 1
                pom = pom + 1
                if broj > 3:
                    return 1

        # dijagonale
        r_pom = row
        c_pom = col
        broj = 0
        while (r_pom - 1) >= 0 and (c_pom - 1) >= 0:
            if not board[r_pom - 1][c_pom - 1] == player:
                break
            r_pom =r_pom - 1
            c_pom =c_pom - 1
        while c_pom < cols and r_pom < rows:
            if not board[r_pom][c_pom] == player:
                break
            r_pom = r_pom + 1
            broj = broj+ 1
            c_pom =c_pom + 1
            if broj >= 4:
                return 1

        r_pom = row
        broj = 0
        c_pom = col
        while  (r_pom + 1) < rows and (c_pom - 1) >= 0:
            if player != board[r_pom + 1][c_pom - 1]:
                break
            r_pom =r_pom + 1
            c_pom =c_pom- 1
        while r_pom >= 0 and c_pom < cols:
            if board[r_pom][c_pom] != player:
                break
            r_pom = r_pom -1
            broj = 1 + broj
            c_pom =c_pom + 1
            if broj > 3:
                return 1
        return 0