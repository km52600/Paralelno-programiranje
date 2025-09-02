import numpy as np
import pyopencl as cl
import pyopencl.array
from pyopencl import mem_flags as flags
from pyopencl import command_queue_properties as properties


def paralel_copy(G, L, psi, psi_tmp, m, n):
    source_path = "copy.cl"
    context = cl.create_some_context(interactive=False)
    queue = cl.CommandQueue(context, properties=properties.PROFILING_ENABLE)

    with open(source_path, "r", encoding="utf-8") as file:
        source = "".join(file.readlines())

    vals = np.array(psi)
    new_vals = np.array(psi_tmp)
    psi_buff = cl.Buffer(
        context, flags.COPY_HOST_PTR | cl.mem_flags.READ_WRITE, hostbuf=vals
    )
    psitmp_buff = cl.Buffer(
        context, cl.mem_flags.READ_WRITE | cl.mem_flags.COPY_HOST_PTR, hostbuf=new_vals
    )

    program = cl.Program(context, source).build()

    num = np.int32(m * n / G)
    kernel = program.copy_vals(
        queue, (G,), (L,), psi_buff, psitmp_buff, np.int32(m), np.int32(n), num
    )
    kernel.wait()
    cl.enqueue_copy(queue, vals, psi_buff).wait()
    return vals