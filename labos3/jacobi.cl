__kernel void jacobi(__global double *psi, __global double *newpsi, const unsigned int m, const unsigned int n, const unsigned int N)
{
    int g_id = get_global_id(0) + 1;

    for (int j = 1; j <= N; j++)
    {
        newpsi[g_id * (m + 2) + j] = 0.25 * (psi[(g_id - 1) * (m + 2) + j] +
                                             psi[(g_id + 1) * (m + 2) + j] +
                                             psi[(g_id) * (m + 2) + j - 1] +
                                             psi[(g_id) * (m + 2) + j + 1]);
    }
}