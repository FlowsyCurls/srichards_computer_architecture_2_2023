#include <stdio.h>
#include <pthread.h>

#define MAX_COUNT 20

int counter = 0;
pthread_mutex_t mutex;
int thread1 = 1, thread2 = 2;

void* increment_counter(void* arg) {
    int i;
    int thread_id = *((int*) arg); // Get the thread ID from the argument
    printf("\nSTART - thread %d \n", thread_id);
    for (i = 0; i < MAX_COUNT; i++) {
        pthread_mutex_lock(&mutex);
        counter++;


        printf("t %d   |  ctr: %d\n", thread_id, counter);
        pthread_mutex_unlock(&mutex);
    }
    printf("END   - thread %d\n", thread_id);
    return NULL;
}

int main() {
    pthread_t t1, t2;

    pthread_mutex_init(&mutex, NULL);

    // Create the threads
    pthread_create(&t1, NULL, increment_counter, (void*) &thread1);
    pthread_create(&t2, NULL, increment_counter, (void*) &thread2);

    // Wait for the threads to finish
    pthread_join(t1, NULL);
    pthread_join(t2, NULL);

    pthread_mutex_destroy(&mutex);

    return 0;
}
