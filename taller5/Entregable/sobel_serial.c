#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <sys/time.h>

#define WIDTH 10000
#define HEIGHT 10000

void sobelSerial(unsigned char *inputImage, unsigned char *outputImage) {
    int i, j, Gx, Gy;
    unsigned char gradient;
    
    for (i = 1; i < HEIGHT - 1; i++) {
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

int main() {
    unsigned char *inputImage = (unsigned char *)malloc(WIDTH * HEIGHT * sizeof(unsigned char));
    unsigned char *outputImage = (unsigned char *)malloc(WIDTH * HEIGHT * sizeof(unsigned char));
    
    struct timeval start, end;
    gettimeofday(&start, NULL);
    
    sobelSerial(inputImage, outputImage);
    
    gettimeofday(&end, NULL);
    double elapsedTime = (end.tv_sec - start.tv_sec) + (end.tv_usec - start.tv_usec) / 1000000.0;
    
    printf("Tiempo de ejecución (serial): %.6f segundos\n", elapsedTime);
    
    free(inputImage);
    free(outputImage);
    
    return 0;
}
