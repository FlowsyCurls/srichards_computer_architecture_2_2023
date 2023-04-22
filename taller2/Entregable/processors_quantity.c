#include <omp.h>

#include <stdio.h>
#include <stdlib.h>


int main(void)
{
    printf("Processors Quantity: %d\n", omp_get_num_procs());

  return 0;
}

// gcc script.c -o script -fopenmp
