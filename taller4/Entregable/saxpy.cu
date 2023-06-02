#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define N 10000000
#define BLOCK_SIZE 256

__global__ void saxpy_kernel(float a, float *x, float *y, int n) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < n) {
        y[i] = a * x[i] + y[i];
    }
}


void saxpy_serial(float a, float* x, float* y, int n)
{
    for (int i = 0; i < n; i++)
    {
        y[i] = a * x[i] + y[i];
    }
}

int main()
{
    float *x, *y, *d_x, *d_y;
    float a = 2.0;
    int size = N * sizeof(float);

    // Allocate memory on host
    x = (float*) malloc(size);
    y = (float*) malloc(size);

    // Initialize vectors on host
    for (int i = 0; i < N; i++)
    {
        x[i] = i;
        y[i] = i * 2;
    }

    // Allocate memory on device
    cudaMalloc((void**) &d_x, size);
    cudaMalloc((void**) &d_y, size);

    // Copy vectors from host to device
    cudaMemcpy(d_x, x, size, cudaMemcpyHostToDevice);
    cudaMemcpy(d_y, y, size, cudaMemcpyHostToDevice);

    // Call serial saxpy
    clock_t t_serial_start = clock();
    saxpy_serial(a, x, y, N);

    clock_t t_serial_end = clock();
    double t_serial = ((double)(t_serial_end - t_serial_start)) / CLOCKS_PER_SEC;

    // Call parallel saxpy
    clock_t t_parallel_start = clock();
    saxpy_kernel<<<(N + BLOCK_SIZE - 1) / BLOCK_SIZE, BLOCK_SIZE>>>(a, d_x, d_y, N);
    cudaDeviceSynchronize();
    clock_t t_parallel_end = clock();
    double t_parallel = ((double)(t_parallel_end - t_parallel_start)) / CLOCKS_PER_SEC;

    // Copy result from device to host
    cudaMemcpy(y, d_y, size, cudaMemcpyDeviceToHost);

    // Free memory on device
    cudaFree(d_x);
    cudaFree(d_y);

    // Print execution times
    printf("Execution for N = %d\n", N);
    printf("Serial time: %f\n", t_serial);
    printf("Parallel time: %f\n", t_parallel);

    // Free memory on host
    free(x);
    free(y);

    return 0;

}