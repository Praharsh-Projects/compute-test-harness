#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

static double now_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec * 1000.0 + (double)ts.tv_nsec / 1.0e6;
}

int main(int argc, char **argv) {
    size_t bytes = 8 * 1024 * 1024;
    int loops = 20;
    if (argc > 1) bytes = (size_t)atoll(argv[1]);
    if (argc > 2) loops = atoi(argv[2]);

    uint8_t *src = (uint8_t *)malloc(bytes);
    uint8_t *dst = (uint8_t *)malloc(bytes);
    if (!src || !dst) {
        fprintf(stderr, "alloc failed\n");
        free(src); free(dst);
        return 1;
    }

    for (size_t i = 0; i < bytes; i++) {
        src[i] = (uint8_t)(i % 251);
        dst[i] = 0;
    }

    double start = now_ms();
    for (int i = 0; i < loops; i++) {
        memcpy(dst, src, bytes);
        uint8_t *tmp = src;
        src = dst;
        dst = tmp;
    }
    double elapsed = now_ms() - start;

    uint64_t checksum = 0;
    for (size_t i = 0; i < bytes; i += 1024) checksum += src[i];

    printf("WORKLOAD=memory_bandwidth\n");
    printf("CHECKSUM=%llu\n", (unsigned long long)checksum);
    printf("ELAPSED_MS=%.3f\n", elapsed);

    free(src); free(dst);
    return 0;
}
