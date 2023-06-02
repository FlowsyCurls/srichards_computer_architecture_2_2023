#include <stdio.h>

#define N 4 


__global__ void matrixMult(float *a, float *b, float *c) {
    int row = blockIdx.y * blockDim.y + threadIdx.y;
    int col = blockIdx.x * blockDim.x + threadIdx.x;
    float sum = 0;

    for (int k = 0; k < N; k++) {
        sum += a[row * N + k] * b[k * N + col];
    }

    c[row * N + col] = sum;
}

int main() {
    float *h_a, *h_b, *h_c; 
    float *d_a, *d_b, *d_c; 

    h_a = (float*) malloc(N * N * sizeof(float));
    h_b = (float*) malloc(N * N * sizeof(float));
    h_c = (float*) malloc(N * N * sizeof(float));

    for (int i = 0; i < N * N; i++) {
        h_a[i] = i;
        h_b[i] = i + 1;
    }

    printf("Matriz a:\n");
    for (int i = 0; i < N * N; i++) {
        printf("%.2f ", h_a[i]);
        if ((i + 1) % N == 0) {
            printf("\n");
        }
    }
    printf("\n");

    printf("Matriz b:\n");
    for (int i = 0; i < N * N; i++) {
        printf("%.2f ", h_b[i]);
        if ((i + 1) % N == 0) {
            printf("\n");
        }
    }
    printf("\n");

    cudaMalloc(&d_a, N * N * sizeof(float));
    cudaMalloc(&d_b, N * N * sizeof(float));
    cudaMalloc(&d_c, N * N * sizeof(float));

    cudaMemcpy(d_a, h_a, N * N * sizeof(float), cudaMemcpyHostToDevice);
    cudaMemcpy(d_b, h_b, N * N * sizeof(float), cudaMemcpyHostToDevice);

    dim3 threadsPerBlock(N, N);
    dim3 numBlocks(1, 1);

    matrixMult<<<numBlocks, threadsPerBlock>>>(d_a, d_b, d_c);

    cudaMemcpy(h_c, d_c, N * N * sizeof(float), cudaMemcpyDeviceToHost);

    printf("Matriz c:\n");
    for (int i = 0; i < N * N; i++) {
        printf("%.2f ", h_c[i]);
        if ((i + 1) % N == 0) {
            printf("\n");
        }
    }

    free(h_a);
    free(h_b);
    free(h_c);
    cudaFree(d_a);
    cudaFree(d_b);
    cudaFree(d_c);

    return 0;
}
