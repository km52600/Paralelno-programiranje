import mpi4py
from mpi4py import MPI
from game import Game
from random import random
from collections import defaultdict
import sys
import copy
from time import time
import math

# tag = 0 -> worker salje prijavu
# tag = 1 -> worker salje rezultate
# tag = 2 -> master salje zadatak workeru
# tag = 3 -> master salje workerima da nema vise zad
# tag = 4 -> master salje stanje workeru
# tag = 5 -> master salje workerima kraj


def get_move(comm, game, depth):
    evals = defaultdict(list)
    best = -1
    best_col = -1
    while depth > 0 and best == -1:
        tasks = get_tasks(game)
        recvd = len(tasks)
        if 0==recvd:
            if comm.size > 0:
                for i in range(1, comm.size):
                    comm.isend("end", dest=i, tag=5).wait()
            return -2
            break

        if comm.size > 1:
            for i in range(1, comm.size):
                comm.isend(copy.deepcopy(game), dest=i, tag=4).wait()

            # primaj rezultate i salji zadatke dok ih ima
            while recvd > 0:
                status = MPI.Status()
                data = comm.recv(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=status)
                dest = status.Get_source()
                tag = status.Get_tag()
                if tag == 0:
                    task = get_next_item(tasks)
                    if None != task:
                        comm.send(obj=task, dest=dest)
                if tag == 1:
                    recvd =recvd - 1
                    parent_w, result_w = data
                    evals[parent_w].append(result_w)

            # nema vise zadataka
            i = 1
            while i < comm.size:
                comm.send("end", dest=i, tag=3)
                i =i + 1
            best, best_col = max_eval_value(evals, best, best_col)
        else:
            for col1, col2 in tasks:
                game.move(col1, Game.CPU)
                if game.game_end(col1):
                    game.undo_move(col1)
                    return col1
                game.move(col2, Game.HUMAN)
                evals[col1].append(eval(game, Game.HUMAN, col2, depth, -1, 1))
                game.undo_move(col2)
                game.undo_move(col1)
            best, best_col = max_eval_value(evals, best, best_col)
    return best_col


def eval(game, player, col, depth, alpha, beta):
    curr_player = game.HUMAN
    if game.game_end(col):
        return -1 if game.CPU != player else 1

    if depth == 0:
        return 0

    if player == game.HUMAN:
        curr_player = game.CPU
    evaluation = 0
    moves_ct = 0
    win_a = 1
    lose_a = 1
    if curr_player == Game.CPU:
        res = -1
        for i in range(1, game.cols + 1):
            if True==game.move_legal(i):
                game.move(i, curr_player)
                new_res = max(res, eval(game, curr_player, i, depth - 1, alpha, beta))
                game.undo_move(i)
                if res<new_res:
                    res = new_res
                    if new_res > -1:
                        lose_a = 0
                    if 1 != new_res:
                        win_a = 0
                    moves_ct = moves_ct + 1
                    evaluation = evaluation + new_res
                alpha = max(alpha, res)
                if beta<=alpha:
                    break

    else:
        res = 1
        for i in range(1, game.cols + 1):
            if game.move_legal(i):
                game.move(i, curr_player)
                new_res = min(res, eval(game, curr_player, i, depth - 1, alpha, beta))
                game.undo_move(i)
                if res > new_res:
                    res = new_res
                    if new_res > -1:
                        lose_a = 0
                    if new_res != 1:
                        win_a = 0
                    moves_ct = moves_ct + 1
                    evaluation = evaluation + new_res
                beta = min(beta, res)
                if beta<=alpha:
                    break
    if lose_a:
        return -1
    elif win_a:
        return 1

    evaluation =evaluation/moves_ct
    return evaluation


def get_next_item(items):
    if len(items) != 0:
        return items.pop()
    elif len(items) == 0:
        return None


def game_finished(comm, game, col, player):
    if game.game_end(col):
        print("Game finished! ({0} won)".format(player))
        i = 1
        while i < comm.size:
            comm.send("end", dest=i, tag=5)
            i += 1
        return 1
    elif False==game.game_end(col):
        return 0


def get_tasks(game):
    return [(col1, col2) for col1 in range(1, game.cols + 1) for col2 in range(1, game.cols + 1) if game.move_legal(col1) and game.move_legal(col2)]


import random
def max_eval_value(evals, best, best_col):
    sorted_columns = sorted(evals.items(), key=lambda x: sum(x[1]) / len(x[1]), reverse=True)
    res_col, res = sorted_columns[0]
    if sum(res) > best or (sum(res) == best and random.random() > 0.5):
        best_col = res_col
        best = sum(res)
    return best, best_col


if __name__ == "__main__":
    comm_mpi = MPI.COMM_WORLD
    process_rank = comm_mpi.Get_rank()

    if process_rank == 0:           # master
        game = Game()
        while 1:
            depth = 7           
            # racunalo na potezu
            start = time()
            best_col = get_move(comm_mpi, game, depth)
            if best_col == -2:
                break
            end = time()
            with open("res.txt", "a+") as f:
                f.write(str(end - start) + "\n")
            game.move(best_col, Game.CPU)
            print("Board after CPU move:")
            game.print_board()
            if game_finished(comm_mpi, game, best_col, "CPU"):
                break

            # covjek na potezu
            while 1:
                try:
                    col = int(input("Upisi stupac > "))
                    if False==game.move_legal(col):
                        raise ValueError()
                    elif False!=game.move_legal(col):
                        break
                except ValueError:
                    print("Moras upisati broj u intervalu [1, 7].")

            game.move(col, Game.HUMAN)
            print("\nBoard after HUMAN move:")
            game.print_board()
            if game_finished(comm_mpi, game, col, "HUMAN"):
                break

    # worker
    else:
        status = MPI.Status()
        while 1:
            rec = comm_mpi.recv(source=0, tag=MPI.ANY_TAG, status=status)
            tag = status.Get_tag()
            depth = 7
            if tag == 5:
                break
            elif tag == 4:
                game_w = rec
            while 1:
                comm_mpi.send(obj="req", dest=0, tag=0)
                data = comm_mpi.recv(source=0, tag=MPI.ANY_TAG, status=status)
                tag = status.Get_tag()
                # vise nema zadataka
                if tag == 3:
                    break
                col1_w, col2_w = data
                game_w.move(col1_w, Game.CPU)

                if False==game_w.game_end(col1_w):
                    game_w.move(col2_w, Game.HUMAN)
                    res_w = eval(game_w, Game.HUMAN, col2_w, depth, -1, 1)
                    game_w.undo_move(col2_w)
                    game_w.undo_move(col1_w)
                    comm_mpi.send(obj=(col1_w, res_w), dest=0, tag=1)
                elif True==game_w.game_end(col1_w):
                    game_w.undo_move(col1_w)
                    comm_mpi.send(obj=(col1_w, 1), dest=0, tag=1)
