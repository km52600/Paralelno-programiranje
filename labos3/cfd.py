import math
import argparse
import time
import numpy as np
import copy
from jacobi import jacobi_step
from jacobi import paralel_jacobi
from jacobi import deltasq
from par_copy import paralel_copy
from jacobi import paralel_deltasq

parser = argparse.ArgumentParser()
parser.add_argument("S", metavar="scale", type=int, nargs=1, help="scale factor")
parser.add_argument("I", metavar="num_iter", type=int, nargs=1, help="number of iters")
parser.add_argument(
    "L", metavar="L_exp", type=int, nargs=1, help="work group size exp", default=8
)


def boundary_psi(psi, m, n, b, h, w):
    for i in range(b + 1, b + w):
        psi[i * (m + 2)] = i - b

    for i in range(b + w, m + 1):
        psi[i * (m + 2)] = w

    for i in range(1, h + 1):
        psi[(m + 1) * (m + 2) + i] = w

    for i in range(h + 1, h + w):
        psi[(m + 1) * (m + 2) + i] = w - i + h

    return psi


if __name__ == "__main__":
    args = parser.parse_args()
    scale_factor = args.S[0]
    num_iter = args.I[0]
    print_freq = 1000
    tol = 0.0
    bbase = 10
    hbase = 15
    wbase = 5
    mbase = 32
    nbase = 32
    irrotational = 1
    checkerr = 0

    if tol > 0:
        checkerr = 1

    if not checkerr:
        print(f"scale factor = {scale_factor}, iterations = {num_iter}")
    else:
        print(f"scale factor = {scale_factor}, iterations = {num_iter}, tol = {tol}")

    b = bbase * scale_factor
    h = hbase * scale_factor
    w = wbase * scale_factor
    m = mbase * scale_factor
    n = nbase * scale_factor

    G = m
    L = 2 ** args.L[0]

    print(f"Running CFD on {m} x {n} grid")

    psi = np.zeros(((m + 2) * (n + 2)))
    psi = boundary_psi(psi, m, n, b, h, w)

    bnorm = psi @ psi.T
    bnorm = math.sqrt(bnorm)

    print("\nStarting main loop...\n")
    t_start = time.time()

    for i in range(1, num_iter + 1):
        # psi_tmp = jacobi_step(psi, m, n)
        psi_tmp = paralel_jacobi(G, L, psi, m, n)

        if checkerr or i == num_iter:
            error = paralel_deltasq(G, L, psi_tmp, psi, m, n)
            # error = deltasq(psi_tmp, psi, m, n)
            error = math.sqrt(error)
            error /= bnorm

        if checkerr:
            if error < tol:
                print(f"Converged on iter {i}")
                break

        # for i in range(1, m + 1):
        #    for j in range(1, n + 1):
        #        psi[i * (m + 2) + j] = psi_tmp[i * (m + 2) + j]
        psi = paralel_copy(G, L, psi, psi_tmp, m, n)

        if i % print_freq == 0:
            if not checkerr:
                print(f"Completed iter {i}")
            else:
                print(f"Completed iter {i}, error = {error}")

    if i > num_iter:
        i = num_iter

    t_stop = time.time()
    t_tot = t_stop - t_start
    t_iter = t_tot / i

    print("... finished")
    print(f"After {i} iterations, the error is {error}")
    print(f"Time for {i} iterations was {t_tot} seconds")
    print(f"Each iteration took {t_iter} seconds")
