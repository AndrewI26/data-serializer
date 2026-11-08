#pragma once

#include <cstddef>
#include <cstring>

#include "schemas.hpp"

// Buffer large enough for any benchmark message; the size of one UDP datagram
// that avoids IP fragmentation (1500 MTU - 20 IP - 8 UDP).
inline constexpr std::size_t kBufSize = 1472;

// A message with every byte set to a non-trivial pattern, so the compiler
// can't treat it as zero-initialized.
template <typename T>
T make_sample() {
    unsigned char bytes[sizeof(T)];
    for (std::size_t i = 0; i < sizeof(T); ++i) {
        bytes[i] = static_cast<unsigned char>(i * 37 + 11);
    }
    T msg;
    std::memcpy(&msg, bytes, sizeof(T));
    return msg;
}
