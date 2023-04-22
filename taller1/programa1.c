#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <unistd.h>
#include <time.h>

#define MAX_SIZE 10

int datos[MAX_SIZE];
int contador = 0;

// Generar numeros aleatorios de 8 bits cada 10 milisegundos y almacernarlo en un arreglo
void *hilo1(void *arg){
    while (1) {
        // Generar un número aleatorio de 8 bits
        int numero = rand() % 256;
        // Verificar si el contador ha llegado al límite
        while (contador >= MAX_SIZE) {
            usleep(10000);
        }
        // Almacenar el número generado en el arreglo
        datos[contador] = numero;
        // Incrementar el contador
        contador++;
        // Dormir durante 10 milisegundos
        usleep(10000);
    }
    pthread_exit(NULL);
}


// Aplicar una operación XOR con el código ASCII de la letra 'S' a 
// cada valor del arreglo "datos" y lo muestra en pantalla cada 1 segundos.
void *hilo2(void *arg){
    while (1) {
        // Aplicar XOR con la S en ASCII a cada valor del arreglo y mostrarlo en pantalla
        printf("\nMuestreo: ");
        for (int i = 0; i < contador; i++) {
            // Aplicar XOR con la letra 'S'
            int xor = datos[i] ^ 'S'; 
            // Imprimir el valor como caracter
            printf("%c ", xor);
        }
        printf("\n");
        // Decrementar el contador después de tomar los valores del arreglo
        contador = 0;
        // Dormir durante 1 segundos
        sleep(1);
    }
    pthread_exit(NULL);
}

int main() {
    srand(time(NULL));
    pthread_t hilo_id1, hilo_id2;
    pthread_create(&hilo_id1, NULL, hilo1, NULL);
    pthread_create(&hilo_id2, NULL, hilo2, NULL);
    pthread_join(hilo_id1, NULL);
    pthread_join(hilo_id2, NULL);
    return 0;
}