#include <iostream>
#include <unordered_map>
#include <chrono>

void benchmark() {
    std::unordered_map<int, int> map;
    const int N = 1000000;

    auto start = std::chrono::high_resolution_clock::now();
    for (int i = 0; i < N; ++i)
        map[i] = i;
    auto mid = std::chrono::high_resolution_clock::now();
    for (int i = 0; i < N; ++i)
        volatile int x = map[i];
    auto end = std::chrono::high_resolution_clock::now();

    std::chrono::duration<double> insert = mid - start;
    std::chrono::duration<double> lookup = end - mid;

    std::cout << "C++ unordered_map insert time: " << insert.count() << "s\n";
    std::cout << "C++ unordered_map lookup time: " << lookup.count() << "s\n";
}

int main() {
    benchmark();
    return 0;
}
