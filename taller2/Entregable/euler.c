#include <stdio.h>
#include <stdlib.h>
#include <omp.h>
#include <time.h>
#include <math.h>

const double euler_real = exp(1);

// Calcula la suma de los términos de la serie de Euler hasta el n-ésimo término en serie (modo serial)
double euler_serial(int n) {
    double euler_sum = 1.0, term = 1.0, fact = 1.0;
    double error;

    for (int i = 1; i <= n; i++) {
        fact *= i;
        term = 1.0 / fact;
        euler_sum += term;
    }
    return euler_sum;

}

// Calcula la suma de los términos de la serie de Euler hasta el n-ésimo término en serie (modo paralelo)
double euler_parallel(int n) {
    double euler_sum = 1.0, term = 1.0, fact = 1.0;
    double error;

    #pragma omp parallel for reduction(*:fact) reduction(+:euler_sum)
    for (int i = 1; i <= n; i++) {
        fact *= i;
        term = 1.0 / fact;
        euler_sum += term;
    }
    return euler_sum;
}


int main() {
    int n[] = {50, 100, 500, 1000, 5000, 10000};
    double e_serial, e_parallel, time_serial, time_parallel;

    printf("n\t\ttiempo\t\teuler\t\t\tpresición\n");
    printf("\033[0;31mvalor real\t\t\t%.16f\033[0m\n", euler_real);
    printf("-----------------------------------------------------------------------------------------------------------------------\n");

    for (int i = 0; i < 6; i++) {
        clock_t start, end;
        double e1,e2,pr1,pr2;

        start = clock();
        e1 = euler_serial(n[i]);
        time_serial = ((double) (clock() - start)) / CLOCKS_PER_SEC;
        
        start = clock();
        e2 = euler_parallel(n[i]);
        time_parallel = ((double) (clock() - start)) / CLOCKS_PER_SEC;

        pr1 = fabs((e1 - euler_real) / euler_real) * 100;
        pr2 = fabs((e2 - euler_real) / euler_real) * 100;

        printf("n=%d\n", n[i]);
        printf("serial:\t\t%f\t%.16f\t%.16f\n", time_serial, e1, pr1);
        printf("paralelo:\t%f\t%.16f\t%.16f\n", time_parallel, e2, pr2);
        printf("-----------------------------------------------------------------------------------------------------------------------\n");
    }

    return 0;
}
