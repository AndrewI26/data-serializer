// End-to-end UDP benchmarks over loopback (127.0.0.1).
//
// Each iteration serializes a message, sends it as one datagram, receives it
// on a second socket and deserializes it. This is single-threaded, so the time
// per iteration is the full send/receive path, dominated by the two system
// calls. Compare against udp_raw (same bytes, no serialization) to see how much
// the generated code contributes.

use std::hint::black_box;
use std::net::UdpSocket;
use std::time::Duration;

use bin_serializer_bench::deserializer::Deserialize;
use bin_serializer_bench::schemas::{Mixed, Tiny, Wide};
use bin_serializer_bench::serializer::Serialize;
use bin_serializer_bench::{BUF_SIZE, make_sample};
use criterion::{BenchmarkGroup, Criterion, Throughput, criterion_group, criterion_main, measurement::WallTime};

type Group<'a> = BenchmarkGroup<'a, WallTime>;

/// A pair of UDP sockets on loopback: `tx` is connected to `rx`.
struct LoopbackPair {
    tx: UdpSocket,
    rx: UdpSocket,
}

impl LoopbackPair {
    fn new() -> Self {
        let rx = UdpSocket::bind("127.0.0.1:0").expect("bind rx");
        // Never block forever if a datagram is dropped.
        rx.set_read_timeout(Some(Duration::from_secs(1))).expect("set timeout");
        let tx = UdpSocket::bind("127.0.0.1:0").expect("bind tx");
        tx.connect(rx.local_addr().expect("rx addr")).expect("connect");
        Self { tx, rx }
    }
}

fn udp_send_recv<T: Serialize + Deserialize>(group: &mut Group, name: &str) {
    let sockets = LoopbackPair::new();
    let msg = make_sample::<T>();
    let mut tx_buf = [0u8; BUF_SIZE];
    let mut rx_buf = [0u8; BUF_SIZE];
    group.throughput(Throughput::Bytes(T::SIZE as u64));
    group.bench_function(name, |b| {
        b.iter(|| {
            let n = msg.serialize(&mut tx_buf).unwrap();
            sockets.tx.send(&tx_buf[..n]).expect("send");
            let got = sockets.rx.recv(&mut rx_buf).expect("recv");
            black_box(T::deserialize(&rx_buf[..got]).expect("short datagram"))
        })
    });
}

// Baseline: same datagrams with no serialize/deserialize calls.
fn udp_raw<T: Serialize + Deserialize>(group: &mut Group, name: &str) {
    let sockets = LoopbackPair::new();
    let mut tx_buf = [0u8; BUF_SIZE];
    let n = make_sample::<T>().serialize(&mut tx_buf).unwrap();
    let mut rx_buf = [0u8; BUF_SIZE];
    group.throughput(Throughput::Bytes(T::SIZE as u64));
    group.bench_function(name, |b| {
        b.iter(|| {
            sockets.tx.send(&tx_buf[..n]).expect("send");
            black_box(sockets.rx.recv(&mut rx_buf).expect("recv"))
        })
    });
}

macro_rules! for_all_schemas {
    ($c:expr, $group_name:literal, $f:ident) => {{
        let mut group = $c.benchmark_group($group_name);
        $f::<Tiny>(&mut group, "Tiny");
        $f::<Mixed>(&mut group, "Mixed");
        $f::<Wide>(&mut group, "Wide");
        group.finish();
    }};
}

fn benches(c: &mut Criterion) {
    for_all_schemas!(c, "udp_raw", udp_raw);
    for_all_schemas!(c, "udp_send_recv", udp_send_recv);
}

criterion_group! {
    name = udp_benches;
    config = Criterion::default()
        .warm_up_time(Duration::from_secs(1))
        .measurement_time(Duration::from_secs(2));
    targets = benches
}
criterion_main!(udp_benches);
