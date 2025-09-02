__kernel void deltasq(__global double *new, __global double *old, __global double *tmp, const unsigned int m, const unsigned int n, const unsigned int N)
{
    int g_id = get_global_id(0) + 1;
    double temp;

    for (int j = 1; j <= N; j++)
    {
        temp = new[g_id * (m + 2) + j] - old[g_id * (m + 2) + j];
        tmp[g_id * (m + 2) + j] = temp * temp;
    }
}