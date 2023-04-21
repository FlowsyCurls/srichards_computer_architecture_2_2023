#include <stdio.h>
#include <stdlib.h>
#include <omp.h>

void initialize_vectors(float *x, float *y, int n) {
    for (int i = 0; i < n; i++) {
        x[i] = (float) rand() / RAND_MAX;
        y[i] = (float) rand() / RAND_MAX;
    }
}

void run_saxpy_serial(float a, float *x, float *y, int n) {
    double start_time = omp_get_wtime();
    for (int i = 0; i < n; i++) {
        y[i] = a * x[i] + y[i];
    }
    double run_time = omp_get_wtime() - start_time;
    printf("Serial   for n=%d     \t%f seconds\n", n, run_time);
}

void run_saxpy_parallel(float a, float *x, float *y, int n) {
    double start_time = omp_get_wtime();
    #pragma omp parallel for
    for (int i = 0; i < n; i++) {
        y[i] = a * x[i] + y[i];
    }
    double run_time = omp_get_wtime() - start_time;
    printf("Parallel for n=%d     \t%f seconds\n\n", n, run_time);
}

int main()
{
    int n1 = 10000;
    int n2 = 100000;
    int n3 = 1000000;
    int n4 = 10000000;
    int n5 = 100000000;

    float a = 2.0;
    float *x, *y;

    // Allocate memory for vectors
    x = (float *) malloc(n5 * sizeof(float));
    y = (float *) malloc(n5 * sizeof(float));

    // Initialize vectors with random values
    initialize_vectors(x, y, n5);

    // Run saxpy for n1
    run_saxpy_serial(a, x, y, n1);
    run_saxpy_parallel(a, x, y, n1);

    // Run saxpy for n2
    run_saxpy_serial(a, x, y, n2);
    run_saxpy_parallel(a, x, y, n2);

    // Run saxpy for n3
    run_saxpy_serial(a, x, y, n3);
    run_saxpy_parallel(a, x, y, n3);

    // Run saxpy for n4
    run_saxpy_serial(a, x, y, n4);
    run_saxpy_parallel(a, x, y, n4);

    // Run saxpy for n5
    run_saxpy_serial(a, x, y, n5);
    run_saxpy_parallel(a, x, y, n5);

    // Free memory
    free(x);
    free(y);

    return 0;
}
