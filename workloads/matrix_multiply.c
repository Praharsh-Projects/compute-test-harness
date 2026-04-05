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
    int n = 96;
    int iterations = 1;

    if (argc > 1) n = atoi(argv[1]);
    if (argc > 2) iterations = atoi(argv[2]);

    size_t size = (size_t)n * (size_t)n;
    float *a = (float *)malloc(size * sizeof(float));
    float *b = (float *)malloc(size * sizeof(float));
    float *c = (float *)malloc(size * sizeof(float));
    if (!a || !b || !c) {
        fprintf(stderr, "alloc failed\n");
        free(a); free(b); free(c);
        return 1;
    }

    for (size_t i = 0; i < size; i++) {
        a[i] = (float)((i % 23) + 1) * 0.1f;
        b[i] = (float)((i % 19) + 1) * 0.2f;
        c[i] = 0.0f;
    }

    double start = now_ms();
    for (int it = 0; it < iterations; it++) {
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                float sum = 0.0f;
                for (int k = 0; k < n; k++) {
                    sum += a[(size_t)i * n + k] * b[(size_t)k * n + j];
                }
                c[(size_t)i * n + j] = sum;
            }
        }
    }
    double elapsed = now_ms() - start;

    double checksum = 0.0;
    for (size_t i = 0; i < size; i++) checksum += c[i];

    printf("WORKLOAD=matrix_multiply\n");
    printf("CHECKSUM=%.4f\n", checksum);
    printf("ELAPSED_MS=%.3f\n", elapsed);

    free(a); free(b); free(c);
    return 0;
}
