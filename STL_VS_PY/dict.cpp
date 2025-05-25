#include <iostream>
#include <unordered_map>
#include <chrono>

int main() {
    const int N = 1000000;
    std::unordered_map<int, int> d;

    // Insert
    auto start = std::chrono::high_resolution_clock::now();
    for (int i = 0; i < N; ++i) {
        d[i] = i;
    }
    auto end = std::chrono::high_resolution_clock::now();
    std::cout << "C++ unordered_map insert time: "
              << std::chrono::duration<double>(end - start).count() << "s\n";

    // Lookup
    start = std::chrono::high_resolution_clock::now();
    for (int i = 0; i < N; ++i) {
        int x = d[i];
    }
    end = std::chrono::high_resolution_clock::now();
    std::cout << "C++ unordered_map lookup time: "
              << std::chrono::duration<double>(end - start).count() << "s\n";
}
