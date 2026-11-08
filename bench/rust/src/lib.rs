// Generated code from bench/bench_schemas.yaml (see build.rs), plus helpers
// shared by the benchmarks.

pub mod schemas {
    include!(concat!(env!("OUT_DIR"), "/schemas.rs"));
}

pub mod serializer {
    include!(concat!(env!("OUT_DIR"), "/serializer.rs"));
}

pub mod deserializer {
    include!(concat!(env!("OUT_DIR"), "/deserializer.rs"));
}

use deserializer::Deserialize;

/// Size of one UDP datagram that avoids IP fragmentation
/// (1500 MTU - 20 IP - 8 UDP). Large enough for every benchmark message.
pub const BUF_SIZE: usize = 1472;

/// A message whose bytes follow a non-trivial pattern (same pattern as the
/// C++ benchmarks), so the compiler can't treat it as all zeros.
pub fn make_sample<T: Deserialize>() -> T {
    let bytes: Vec<u8> = (0..T::SIZE).map(|i| (i * 37 + 11) as u8).collect();
    T::deserialize(&bytes).expect("sample buffer is exactly T::SIZE bytes")
}

#[cfg(test)]
mod tests {
    use super::schemas::*;
    use super::serializer::Serialize;
    use super::*;

    #[test]
    fn round_trip_and_wire_format() {
        let msg = Mixed {
            f_u8: 200,
            f_u64: 0x1122_3344_5566_7788,
            f_i16: -3,
            f_f64: 3.25,
            f_i8: -1,
            f_u32: 0xDEAD_BEEF,
            f_i64: -42,
            f_u16: 0xBEEF,
            f_f32: 1.5,
            f_i32: -7,
        };
        let mut buf = [0u8; BUF_SIZE];
        assert_eq!(msg.serialize(&mut buf), Some(42));
        assert_eq!(msg.serialize(&mut buf[..41]), None);

        // Packed, little-endian: f_u8 at offset 0, then f_u64's low byte.
        assert_eq!(buf[0], 200);
        assert_eq!(buf[1], 0x88);

        assert_eq!(Mixed::deserialize(&buf[..42]), Some(msg));
        assert_eq!(Mixed::deserialize(&buf[..41]), None);
    }
}
