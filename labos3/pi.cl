__kernel void pi(__global double *sums, const int N)
{
    int global_id = get_global_id(0);
    int size = get_global_size(0);
    double h = 1.0 / (double)N;
    double x;
    double res;
    double my_sum = 0.0;

    for (int i = global_id + 1; i <= N; i += size)
    {
        x = h * ((double)i - 0.5);
        my_sum += 4.0 / (1.0 + x * x);
    }
    sums[global_id] = h * my_sum;
}