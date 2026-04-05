#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

static double now_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec * 1000.0 + (double)ts.tv_nsec / 1.0e6;
}

int main(int argc, char **argv) {
    int n = 1000000;
    if (argc > 1) n = atoi(argv[1]);

    float *a = (float *)malloc((size_t)n * sizeof(float));
    float *b = (float *)malloc((size_t)n * sizeof(float));
    float *c = (float *)malloc((size_t)n * sizeof(float));
    if (!a || !b || !c) {
        fprintf(stderr, "alloc failed\n");
        free(a); free(b); free(c);
        return 1;
    }

    for (int i = 0; i < n; i++) {
        a[i] = (float)((i % 101) * 0.1);
        b[i] = (float)((i % 97) * 0.2);
    }

    double start = now_ms();
    for (int i = 0; i < n; i++) {
        c[i] = a[i] + b[i];
    }
    double elapsed = now_ms() - start;

    double checksum = 0.0;
    for (int i = 0; i < n; i += 31) checksum += c[i];

    printf("WORKLOAD=vector_add\n");
    printf("CHECKSUM=%.4f\n", checksum);
    printf("ELAPSED_MS=%.3f\n", elapsed);

    free(a); free(b); free(c);
    return 0;
}
