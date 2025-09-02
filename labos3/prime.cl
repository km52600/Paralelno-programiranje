__kernel void prime_number(__global int *values, __global int *ct, const unsigned int N)
{
    int global_id = get_global_id(0);
    int size = get_global_size(0);
    int prime;
    int number;

    for (int j = 0; j < N; j++)
    {
        prime = 1;
        number = values[global_id * N + j];

        if (number < 2)
            prime = 0;

        int rt = (int)sqrt((float)number);
        for (int i = 2; i <= rt; i++)
        {
            if (number % i == 0)
            {
                prime = 0;
                break;
            }
        }

        // values[global_id * N + j] = prime;

        if (prime)
            atomic_inc(ct);
    }
}