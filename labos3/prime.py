import time
import numpy as np
import argparse
import pyopencl as cl
import pyopencl.array
from pyopencl.reduction import ReductionKernel
from pyopencl import mem_flags as flags
from pyopencl import command_queue_properties as properties

parser = argparse.ArgumentParser()
parser.add_argument("N", metavar="N_exp", type=int, nargs=1, help="array size exp")
parser.add_argument("G", metavar="G_exp", type=int, nargs=1, help="global size exp")
parser.add_argument("L", metavar="L_exp", type=int, nargs=1, help="work group size exp")


if __name__ == "__main__":
    source_path = "prime.cl"

    args = parser.parse_args()
    N = 2 ** args.N[0]
    G = 2 ** args.G[0]
    L = 2 ** args.L[0]

    # stvaranje konteksta
    context = cl.create_some_context(interactive=False)

    # stvaranje reda izvodenja
    queue = cl.CommandQueue(context, properties=properties.PROFILING_ENABLE)

    with open(source_path, "r", encoding="utf-8") as file:
        source = "".join(file.readlines())

    # stvaranje strukture podataka
    # sadrzaj se automatski kopira u memoriju uredaja
    seq = np.arange(start=0, stop=N, dtype=np.int32)
    ct = np.array([0])
    buffer = cl.Buffer(context, flags.COPY_HOST_PTR, hostbuf=seq)
    res = cl.Buffer(context, flags.WRITE_ONLY, ct.nbytes)

    # stvaranje programa i ucitavanje programa kernela
    program = cl.Program(context, source).build()

    kernel = program.prime_number(queue, (G,), (L,), buffer, res, np.int32(N / G))
    kernel.wait()
    cl.enqueue_copy(queue, ct, res).wait()

    print("Prime numbers:", ct[0])
    t = (kernel.profile.end - kernel.profile.start) * 1e-9
    print(f"G:2^{args.G[0]:<5}  L:2^{args.L[0]:<5} Time: {t:<10.8f}")
    # with open("prime_res.txt", "a+") as f:
    #    f.write("G: " + str(G) + " L: " + str(L) + " Time: " + str(t) + "\n")