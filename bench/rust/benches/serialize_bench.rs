// Microbenchmarks for the generated serialize/deserialize functions.
//
// These calls are only a few instructions each, so compare them against the
// raw byte-copy baseline: the gap is the overhead the generated code adds.

use std::hint::black_box;
use std::time::Duration;

use bin_serializer_bench::deserializer::Deserialize;
use bin_serializer_bench::schemas::{Mixed, Tiny, Wide};
use bin_serializer_bench::serializer::Serialize;
use bin_serializer_bench::{BUF_SIZE, make_sample};
use criterion::{BenchmarkGroup, Criterion, Throughput, criterion_group, criterion_main, measurement::WallTime};

type Group<'a> = BenchmarkGroup<'a, WallTime>;

// Baseline: copy SIZE bytes with no length check, no per-field work.
fn memcpy_baseline<T: Serialize + Deserialize>(group: &mut Group, name: &str) {
    let mut src = [0u8; BUF_SIZE];
    make_sample::<T>().serialize(&mut src).unwrap();
    let mut dst = [0u8; BUF_SIZE];
    group.throughput(Throughput::Bytes(T::SIZE as u64));
    group.bench_function(name, |b| {
        b.iter(|| {
            black_box(&mut dst)[..T::SIZE].copy_from_slice(&black_box(&src)[..T::SIZE]);
        })
    });
}

fn serialize<T: Serialize + Deserialize>(group: &mut Group, name: &str) {
    let msg = make_sample::<T>();
    let mut buf = [0u8; BUF_SIZE];
    group.throughput(Throughput::Bytes(T::SIZE as u64));
    group.bench_function(name, |b| {
        b.iter(|| black_box(&msg).serialize(black_box(&mut buf)))
    });
}

fn deserialize<T: Serialize + Deserialize>(group: &mut Group, name: &str) {
    let mut buf = [0u8; BUF_SIZE];
    let len = make_sample::<T>().serialize(&mut buf).unwrap();
    group.throughput(Throughput::Bytes(T::SIZE as u64));
    group.bench_function(name, |b| {
        b.iter(|| T::deserialize(&black_box(&buf)[..black_box(len)]))
    });
}

fn round_trip<T: Serialize + Deserialize>(group: &mut Group, name: &str) {
    let msg = make_sample::<T>();
    let mut buf = [0u8; BUF_SIZE];
    group.throughput(Throughput::Bytes(2 * T::SIZE as u64));
    group.bench_function(name, |b| {
        b.iter(|| {
            let n = black_box(&msg).serialize(&mut buf).unwrap();
            T::deserialize(&black_box(&buf)[..n])
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
    for_all_schemas!(c, "memcpy_baseline", memcpy_baseline);
    for_all_schemas!(c, "serialize", serialize);
    for_all_schemas!(c, "deserialize", deserialize);
    for_all_schemas!(c, "round_trip", round_trip);
}

criterion_group! {
    name = serialize_benches;
    config = Criterion::default()
        .warm_up_time(Duration::from_secs(1))
        .measurement_time(Duration::from_secs(2));
    targets = benches
}
criterion_main!(serialize_benches);
