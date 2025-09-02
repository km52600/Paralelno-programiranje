import time
import numpy as np
import argparse
import pyopencl as cl
import pyopencl.array
from pyopencl.reduction import ReductionKernel
from pyopencl import mem_flags as flags
from pyopencl import command_queue_properties as properties

parser = argparse.ArgumentParser()
parser.add_argument("N", metavar="N", type=int, nargs=1, help="seq size exp")
parser.add_argument("G", metavar="G_exp", type=int, nargs=1, help="global size exp")
parser.add_argument("L", metavar="L_exp", type=int, nargs=1, help="work group size exp")


if __name__ == "__main__":
    source_path = "pi.cl"

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
    sums = np.zeros(G)
    buffer = cl.Buffer(context, flags.COPY_HOST_PTR, hostbuf=sums)

    # stvaranje programa i ucitavanje programa kernela
    program = cl.Program(context, source).build()

    kernel = program.pi(queue, (G,), (L,), buffer, np.int32(N))
    kernel.wait()
    cl.enqueue_copy(queue, sums, buffer).wait()

    # print("pi:", np.sum(sums))
    pi = np.sum(sums)
    t = (kernel.profile.end - kernel.profile.start) * 1e-9
    print(f"G:2^{args.G[0]:<5}  L:2^{args.L[0]:<5} Time: {t:<10.8f} pi: {pi:15}")
    #with open("pi_res.txt", "a+") as f:
    #    f.write(
    #        "G: " + str(G) + " L: " + str(L) + " Time: " + str(t) +" pi: " + str(pi) + "\n"
    #    )