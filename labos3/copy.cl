__kernel void copy_vals(__global double *psi, __global double *newpsi, const unsigned int m, const unsigned int n, const unsigned int N)
{
    int g_id = get_global_id(0) + 1;

    for (int j = 1; j <= N; j++)
    {
        psi[g_id * (m + 2) + j] = newpsi[g_id * (m + 2) + j];
    }
}