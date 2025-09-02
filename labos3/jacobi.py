import numpy as np
import pyopencl as cl
import pyopencl.array
from pyopencl import mem_flags as flags
from pyopencl import command_queue_properties as properties


def jacobi_step(psi, m, n):
    psinew = np.zeros(((m + 2) * (n + 2)))
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            psinew[i * (m + 2) + j] = 0.25 * (
                psi[(i - 1) * (m + 2) + j]
                + psi[(i + 1) * (m + 2) + j]
                + psi[i * (m + 2) + j - 1]
                + psi[i * (m + 2) + j + 1]
            )
    return psinew


def paralel_jacobi(G, L, psi, m, n):
    source_path = "jacobi.cl"
    context = cl.create_some_context(interactive=False)
    queue = cl.CommandQueue(context, properties=properties.PROFILING_ENABLE)

    with open(source_path, "r", encoding="utf-8") as file:
        source = "".join(file.readlines())

    vals = np.array(psi)
    new_vals = np.zeros(psi.shape[0])
    buffer = cl.Buffer(context, flags.COPY_HOST_PTR | flags.READ_ONLY, hostbuf=vals)
    res_buffer = cl.Buffer(context, flags.READ_WRITE, new_vals.nbytes)

    program = cl.Program(context, source).build()

    num = np.int32(m * n / G)
    kernel = program.jacobi(
        queue, (G,), (L,), buffer, res_buffer, np.int32(m), np.int32(n), num
    )
    kernel.wait()
    cl.enqueue_copy(queue, new_vals, res_buffer).wait()
    return new_vals


def deltasq(newarr, oldarr, m, n):
    dsq = 0.0

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            tmp = newarr[i * (m + 2) + j] - oldarr[i * (m + 2) + j]
            dsq += tmp * tmp

    return dsq


def paralel_deltasq(G, L, newarr, oldarr, m, n):
    source_path = "deltasq.cl"
    context = cl.create_some_context(interactive=False)
    queue = cl.CommandQueue(context, properties=properties.PROFILING_ENABLE)

    with open(source_path, "r", encoding="utf-8") as file:
        source = "".join(file.readlines())

    new = np.array(newarr)
    old = np.array(oldarr)
    tmp = np.zeros(newarr.shape[0], dtype=np.double)

    new_buff = cl.Buffer(context, flags.COPY_HOST_PTR | flags.READ_ONLY, hostbuf=new)
    old_buff = cl.Buffer(context, flags.COPY_HOST_PTR | flags.READ_ONLY, hostbuf=old)
    tmp_buff = cl.Buffer(context, flags.COPY_HOST_PTR | flags.WRITE_ONLY, hostbuf=tmp)

    program = cl.Program(context, source).build()

    num = np.int32(m * n / G)
    kernel = program.deltasq(
        queue, (G,), (L,), new_buff, old_buff, tmp_buff, np.int32(m), np.int32(n), num
    )
    kernel.wait()
    cl.enqueue_copy(queue, tmp, tmp_buff).wait()
    return np.sum(tmp)