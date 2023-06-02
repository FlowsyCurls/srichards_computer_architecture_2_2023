#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <sys/time.h>
#include <mpi.h>

#define WIDTH 10000
#define HEIGHT 10000

void sobelParallel(unsigned char *inputImage, unsigned char *outputImage, int startRow, int endRow) {
    int i, j, Gx, Gy;
    unsigned char gradient;
    
    for (i = startRow; i < endRow; i++) {
        for (j = 1; j < WIDTH - 1; j++) {
            Gx = inputImage[(i - 1) * WIDTH + (j + 1)] + 2 * inputImage[i * WIDTH + (j + 1)] + inputImage[(i + 1) * WIDTH + (j + 1)] -
                 inputImage[(i - 1) * WIDTH + (j - 1)] - 2 * inputImage[i * WIDTH + (j - 1)] - inputImage[(i + 1) * WIDTH + (j - 1)];
            
            Gy = inputImage[(i + 1) * WIDTH + (j - 1)] + 2 * inputImage[(i + 1) * WIDTH + j] + inputImage[(i + 1) * WIDTH + (j + 1)] -
                 inputImage[(i - 1) * WIDTH + (j - 1)] - 2 * inputImage[(i - 1) * WIDTH + j] - inputImage[(i - 1) * WIDTH + (j + 1)];
            
            gradient = (unsigned char)(sqrt(Gx * Gx + Gy * Gy) / 2);
            
            outputImage[i * WIDTH + j] = gradient;
        }
    }
}

int main(int argc, char *argv[]) {
    int rank, numProcs;
    int startRow, endRow, numRowsPerProc;
    unsigned char *inputImage, *outputImage;
    
    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &numProcs);
    
    numRowsPerProc = HEIGHT / numProcs;
    startRow = rank * numRowsPerProc;
    endRow = startRow + numRowsPerProc;
    
    if (rank == 0) {
        inputImage = (unsigned char *)malloc(WIDTH * HEIGHT * sizeof(unsigned char));
        outputImage = (unsigned char *)malloc(WIDTH * HEIGHT * sizeof(unsigned char));
    }
    else {
        inputImage = (unsigned char *)malloc(WIDTH * numRowsPerProc * sizeof(unsigned char));
        outputImage = (unsigned char *)malloc(WIDTH * numRowsPerProc * sizeof(unsigned char));
    }
    
    struct timeval start, end;
    gettimeofday(&start, NULL);
    
    MPI_Bcast(inputImage, WIDTH * HEIGHT, MPI_UNSIGNED_CHAR, 0, MPI_COMM_WORLD);
    
    sobelParallel(inputImage, outputImage, startRow, endRow);
    
    unsigned char *receiveBuffer = NULL;
    if (rank == 0) {
        receiveBuffer = (unsigned char *)malloc(WIDTH * HEIGHT * sizeof(unsigned char));
    }

    MPI_Gather(outputImage + startRow * WIDTH, WIDTH * numRowsPerProc, MPI_UNSIGNED_CHAR,
            receiveBuffer + startRow * WIDTH, WIDTH * numRowsPerProc, MPI_UNSIGNED_CHAR, 0, MPI_COMM_WORLD);

    if (rank == 0) {
        // Liberar receiveBuffer y otros procesamientos
        free(receiveBuffer);
    }
        
    gettimeofday(&end, NULL);
    
    if (rank == 0) {
        double elapsedTime = (end.tv_sec - start.tv_sec) + (end.tv_usec - start.tv_usec) / 1000000.0;
        printf("Tiempo de ejecución (paralelo): %.6f segundos\n", elapsedTime);
        
        free(inputImage);
        free(outputImage);
    }
    
    MPI_Finalize();
    
    return 0;
}
