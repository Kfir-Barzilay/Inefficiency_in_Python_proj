#include <Python.h>
#include <time.h>
#include <stdlib.h>
#include <stdio.h>

#define N 1000000

static double elapsed(struct timespec start, struct timespec end) {
    return (end.tv_sec - start.tv_sec) + (end.tv_nsec - start.tv_nsec) / 1e9;
}

int main(int argc, char *argv[]) {
    Py_Initialize();
    PyObject *dict = PyDict_New();
    if (!dict) {
        fprintf(stderr, "Failed to create dict");
        return 1;
    }

    PyObject *key, *value;
    struct timespec t0, t1;

    // Prepare random keys
    int *keys = malloc(N * sizeof(int));
    for (int i = 0; i < N; ++i) keys[i] = rand() % (N * 10);

    // Insertion
    clock_gettime(CLOCK_MONOTONIC, &t0);
    for (int i = 0; i < N; ++i) {
        key = PyLong_FromLong(keys[i]);
        value = PyLong_FromLong(keys[i]);
        PyDict_SetItem(dict, key, value);
        Py_DECREF(key); Py_DECREF(value);
    }
    clock_gettime(CLOCK_MONOTONIC, &t1);
    printf(" insert: %.4f seconds", elapsed(t0, t1));

    // Lookup
    volatile long v = 0;
    clock_gettime(CLOCK_MONOTONIC, &t0);
    for (int i = 0; i < N; ++i) {
        key = PyLong_FromLong(keys[i]);
        value = PyDict_GetItem(dict, key);
        v ^= PyLong_AsLong(value);
        Py_DECREF(key);
    }
    clock_gettime(CLOCK_MONOTONIC, &t1);
    printf(" lookup: %.4f seconds", elapsed(t0, t1));

    // Deletion
    clock_gettime(CLOCK_MONOTONIC, &t0);
    for (int i = 0; i < N; ++i) {
        key = PyLong_FromLong(keys[i]);
        PyDict_DelItem(dict, key);
        Py_DECREF(key);
    }
    clock_gettime(CLOCK_MONOTONIC, &t1);
    printf(" delete: %.4f seconds", elapsed(t0, t1));

    free(keys);
    Py_DECREF(dict);
    Py_Finalize();
    return 0;
}