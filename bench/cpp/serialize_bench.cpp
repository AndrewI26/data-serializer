// Microbenchmarks for the generated serialize/deserialize functions.
//
// These calls are only a few instructions each, so compare them against the
// raw memcpy baseline: the gap is the overhead the generated code adds.

#include <benchmark/benchmark.h>

#include <cstring>

#include "bench_common.hpp"
#include "deserializer.hpp"
#include "serializer.hpp"

template <typename T>
static void BM_Serialize(benchmark::State& state) {
    T msg = make_sample<T>();
    alignas(64) std::byte buf[kBufSize];
    for (auto _ : state) {
        benchmark::DoNotOptimize(msg);
        std::size_t n = serialize(msg, buf, sizeof(buf));
        benchmark::DoNotOptimize(n);
        benchmark::DoNotOptimize(buf);
        benchmark::ClobberMemory();
    }
    state.SetItemsProcessed(state.iterations());
    state.SetBytesProcessed(state.iterations() * static_cast<int64_t>(sizeof(T)));
}

template <typename T>
static void BM_Deserialize(benchmark::State& state) {
    alignas(64) std::byte buf[kBufSize];
    std::size_t len = serialize(make_sample<T>(), buf, sizeof(buf));
    for (auto _ : state) {
        benchmark::DoNotOptimize(buf);
        benchmark::DoNotOptimize(len);
        auto msg = deserialize<T>(buf, len);
        benchmark::DoNotOptimize(msg);
    }
    state.SetItemsProcessed(state.iterations());
    state.SetBytesProcessed(state.iterations() * static_cast<int64_t>(sizeof(T)));
}

template <typename T>
static void BM_RoundTrip(benchmark::State& state) {
    T msg = make_sample<T>();
    alignas(64) std::byte buf[kBufSize];
    for (auto _ : state) {
        benchmark::DoNotOptimize(msg);
        std::size_t n = serialize(msg, buf, sizeof(buf));
        benchmark::ClobberMemory();
        auto out = deserialize<T>(buf, n);
        benchmark::DoNotOptimize(out);
    }
    state.SetItemsProcessed(state.iterations());
    state.SetBytesProcessed(state.iterations() * static_cast<int64_t>(2 * sizeof(T)));
}

// Baseline: a bare memcpy of the struct with no length check or optional.
template <typename T>
static void BM_MemcpyBaseline(benchmark::State& state) {
    T msg = make_sample<T>();
    alignas(64) std::byte buf[kBufSize];
    for (auto _ : state) {
        benchmark::DoNotOptimize(msg);
        std::memcpy(buf, &msg, sizeof(T));
        benchmark::DoNotOptimize(buf);
        benchmark::ClobberMemory();
    }
    state.SetItemsProcessed(state.iterations());
    state.SetBytesProcessed(state.iterations() * static_cast<int64_t>(sizeof(T)));
}

#define BENCH_ALL_SCHEMAS(fn)       \
    BENCHMARK_TEMPLATE(fn, Tiny);   \
    BENCHMARK_TEMPLATE(fn, Mixed);  \
    BENCHMARK_TEMPLATE(fn, Wide)

BENCH_ALL_SCHEMAS(BM_MemcpyBaseline);
BENCH_ALL_SCHEMAS(BM_Serialize);
BENCH_ALL_SCHEMAS(BM_Deserialize);
BENCH_ALL_SCHEMAS(BM_RoundTrip);
