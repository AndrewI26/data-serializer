// End-to-end UDP benchmarks over loopback (127.0.0.1).
//
// Each iteration serializes a message, sends it as one datagram, receives it
// on a second socket and deserializes it. This is single-threaded, so the time
// per iteration is the CPU cost of the full send/receive path, dominated by the
// two system calls. Compare against BM_UdpRaw* (same bytes, no serialization)
// to see how much the generated code contributes.

#include <benchmark/benchmark.h>

#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <unistd.h>

#include <cerrno>
#include <cstring>
#include <string>

#include "bench_common.hpp"
#include "deserializer.hpp"
#include "serializer.hpp"

namespace {

// A pair of UDP sockets on loopback: `tx` is connected to `rx`.
class LoopbackPair {
public:
    LoopbackPair() {
        rx_ = ::socket(AF_INET, SOCK_DGRAM, 0);
        tx_ = ::socket(AF_INET, SOCK_DGRAM, 0);
        if (rx_ < 0 || tx_ < 0) {
            fail("socket");
            return;
        }

        int buf_size = 4 * 1024 * 1024;
        ::setsockopt(rx_, SOL_SOCKET, SO_RCVBUF, &buf_size, sizeof(buf_size));
        ::setsockopt(tx_, SOL_SOCKET, SO_SNDBUF, &buf_size, sizeof(buf_size));

        // Never block forever if a datagram is dropped.
        timeval timeout{1, 0};
        ::setsockopt(rx_, SOL_SOCKET, SO_RCVTIMEO, &timeout, sizeof(timeout));

        sockaddr_in addr{};
        addr.sin_family = AF_INET;
        addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
        addr.sin_port = 0;  // let the OS pick a free port
        if (::bind(rx_, reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) < 0) {
            fail("bind");
            return;
        }
        socklen_t len = sizeof(addr);
        if (::getsockname(rx_, reinterpret_cast<sockaddr*>(&addr), &len) < 0) {
            fail("getsockname");
            return;
        }
        if (::connect(tx_, reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) < 0) {
            fail("connect");
            return;
        }
    }

    ~LoopbackPair() {
        if (rx_ >= 0) ::close(rx_);
        if (tx_ >= 0) ::close(tx_);
    }

    LoopbackPair(const LoopbackPair&) = delete;
    LoopbackPair& operator=(const LoopbackPair&) = delete;

    bool ok() const { return error_.empty(); }
    const std::string& error() const { return error_; }
    int rx() const { return rx_; }
    int tx() const { return tx_; }

private:
    void fail(const char* what) { error_ = std::string(what) + ": " + std::strerror(errno); }

    int rx_ = -1;
    int tx_ = -1;
    std::string error_;
};

}  // namespace

template <typename T>
static void BM_UdpSendRecv(benchmark::State& state) {
    LoopbackPair sockets;
    if (!sockets.ok()) {
        state.SkipWithError(sockets.error());
        return;
    }

    const T msg = make_sample<T>();
    alignas(64) std::byte tx_buf[kBufSize];
    alignas(64) std::byte rx_buf[kBufSize];

    for (auto _ : state) {
        std::size_t n = serialize(msg, tx_buf, sizeof(tx_buf));
        if (::send(sockets.tx(), tx_buf, n, 0) != static_cast<ssize_t>(n)) {
            state.SkipWithError(std::string("send: ") + std::strerror(errno));
            break;
        }
        ssize_t got = ::recv(sockets.rx(), rx_buf, sizeof(rx_buf), 0);
        if (got < 0) {
            state.SkipWithError(std::string("recv: ") + std::strerror(errno));
            break;
        }
        auto out = deserialize<T>(rx_buf, static_cast<std::size_t>(got));
        if (!out) {
            state.SkipWithError("short datagram");
            break;
        }
        benchmark::DoNotOptimize(out);
    }
    state.SetItemsProcessed(state.iterations());
    state.SetBytesProcessed(state.iterations() * static_cast<int64_t>(sizeof(T)));
}

// Baseline: same datagrams with no serialize/deserialize calls.
template <typename T>
static void BM_UdpRawSendRecv(benchmark::State& state) {
    LoopbackPair sockets;
    if (!sockets.ok()) {
        state.SkipWithError(sockets.error());
        return;
    }

    const T msg = make_sample<T>();
    alignas(64) std::byte tx_buf[kBufSize];
    alignas(64) std::byte rx_buf[kBufSize];
    std::memcpy(tx_buf, &msg, sizeof(T));

    for (auto _ : state) {
        if (::send(sockets.tx(), tx_buf, sizeof(T), 0) != static_cast<ssize_t>(sizeof(T))) {
            state.SkipWithError(std::string("send: ") + std::strerror(errno));
            break;
        }
        ssize_t got = ::recv(sockets.rx(), rx_buf, sizeof(rx_buf), 0);
        if (got < 0) {
            state.SkipWithError(std::string("recv: ") + std::strerror(errno));
            break;
        }
        benchmark::DoNotOptimize(rx_buf);
    }
    state.SetItemsProcessed(state.iterations());
    state.SetBytesProcessed(state.iterations() * static_cast<int64_t>(sizeof(T)));
}

#define BENCH_ALL_SCHEMAS(fn)       \
    BENCHMARK_TEMPLATE(fn, Tiny);   \
    BENCHMARK_TEMPLATE(fn, Mixed);  \
    BENCHMARK_TEMPLATE(fn, Wide)

BENCH_ALL_SCHEMAS(BM_UdpRawSendRecv);
BENCH_ALL_SCHEMAS(BM_UdpSendRecv);
