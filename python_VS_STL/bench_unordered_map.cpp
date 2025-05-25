#include <unordered_map>
#include <vector>
#include <random>
#include <chrono>
#include <iostream>

using Clock = std::chrono::high_resolution_clock;
using Duration = std::chrono::duration<double>;

int main() {
    const size_t N = 1000000;
    std::vector<int> keys(N);
    std::mt19937_64 rng(12345);
    std::uniform_int_distribution<int> dist(0, N * 10);
    for (auto &k : keys) k = dist(rng);

    std::unordered_map<int, int> m;
    m.reserve(N);

    // Insert
    auto t0 = Clock::now();
    for (auto k : keys) m[k] = k;
    auto t1 = Clock::now();

    // Lookup
    volatile int v = 0;
    auto t2 = Clock::now();
    for (auto k : keys) v ^= m[k];
    auto t3 = Clock::now();

    // Delete
    for (auto k : keys) m.erase(k);
    auto t4 = Clock::now();

    Duration d_insert = t1 - t0;
    Duration d_lookup = t3 - t2;
    Duration d_delete = t4 - t3;

    std::cout << " insert: " << d_insert.count() << " seconds";
    std::cout << " lookup: " << d_lookup.count() << " seconds";
    std::cout << " delete: " << d_delete.count() << " seconds";
    return 0;
}