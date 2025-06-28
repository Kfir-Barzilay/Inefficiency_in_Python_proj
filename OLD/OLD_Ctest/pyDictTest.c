#include <Python.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define NUM_KEYS 512  // Enough to fit keys in 32KiB L1 assuming no extra structure overhead

void test_custom_dict_function(void) {
    PyObject *dict = PyDict_New();
    PyObject *keys[NUM_KEYS];
    PyObject *vals[NUM_KEYS];
    int i;

    // Warm up: ensure memory gets allocated (helps cache alignment too)
    for (i = 0; i < NUM_KEYS; ++i) {
        char buf[32];
        snprintf(buf, sizeof(buf), "key_%d", i);
        keys[i] = PyUnicode_FromString(buf);
        vals[i] = PyLong_FromLong(i);
        PyDict_SetItem(dict, keys[i], vals[i]);
    }

    // Shuffle keys to randomize access pattern
    srand(time(NULL));
    for (i = 0; i < NUM_KEYS; ++i) {
        int j = rand() % NUM_KEYS;
        PyObject *tmp = keys[i];
        keys[i] = keys[j];
        keys[j] = tmp;
    }

    // Access all keys (should hit cache if all fits in L1)
    clock_t start = clock();
    for (i = 0; i < NUM_KEYS; ++i) {
        PyObject *result = PyDict_GetItem(dict, keys[i]);
        if (!result) {
            printf("Missing key!\n");
        }
    }
    clock_t end = clock();

    double elapsed_ms = 1000.0 * (end - start) / CLOCKS_PER_SEC;
    printf("Accessed %d keys in %.3f ms\n", NUM_KEYS, elapsed_ms);

    // Cleanup
    for (i = 0; i < NUM_KEYS; ++i) {
        Py_DECREF(keys[i]);
        Py_DECREF(vals[i]);
    }
    Py_DECREF(dict);
}
