import argparse
import time

parser = argparse.ArgumentParser()
parser.add_argument("N", metavar="N", type=int, nargs=1, help="seq size exp")


if __name__ == "__main__":
    args = parser.parse_args()
    N = 2 ** args.N[0]
    h = 1.0 / N
    suma = 0.0

    t1 = time.time()
    for i in range(N):
        x = h * (i - 0.5)
        suma += 4.0 / (1.0 + x * x)
    pi = h * suma
    t2 = time.time()
    print("pi:", pi)
    print("Time", t2 - t1)