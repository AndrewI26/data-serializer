# Binary Order Entry (BOE) Codegen

Data serilization framework for high performance applications.

Define the shape of your data in a yaml file then use the python library to generate code for serilzation and deserilzation in C++ or Rust.

## Running the project

```bash
uv sync
uv run schema-serializer examples/simple.yaml            # C++ (default)
uv run schema-serializer examples/simple.yaml -t rust    # Rust
```

Both targets produce the same wire format: fields in declared order, packed with no padding, little-endian.

## Schema Options

Every schema must be organized as follows:

```yaml
schemas:
  - name: <schema_name>
    fields:
      - name: <field_name>
        type: <type>
      - name: <field_name>
        type: <type>
  - name: <schema_name>
    fields:
      - name: <field_name>
        type: <type>
      - name: <field_name>
        type: <type>
```

`<schema_name>` and `<field_name>` can be replaced with any string of chars and `_`, no spaces. These will be the field names used on the deserialized data.

| Type | Size | Description |
| ------ | ------ | ------------- |
| `char` | 1 bytes | ASCII 8-bit charecter |
| `u8` | 1 byte | Unsigned 8-bit integer |
| `u16` | 2 bytes | Unsigned 16-bit integer |
| `u32` | 4 bytes | Unsigned 32-bit integer |
| `u64` | 8 bytes | Unsigned 64-bit integer |
| `i8` | 1 byte | Signed 8-bit integer |
| `i16` | 2 bytes | Signed 16-bit integer |
| `i32` | 4 bytes | Signed 32-bit integer |
| `i64` | 8 bytes | Signed 64-bit integer |
| `f32` | 4 bytes | 32-bit floating-point number |
| `f64` | 8 bytes | 64-bit floating-point number |

## Benchmarks

Benchmarks live in `bench/`, with one subfolder per target language. All languages share the message definitions in `bench/bench_schemas.yaml`, and each build regenerates its code from that schema whenever the schema, templates or generator change.

```bash
uv run bench             # build, then run all benchmarks in both languages
uv run bench serialize   # serialize/deserialize vs. a raw byte-copy baseline
uv run bench udp         # full send/receive over loopback UDP
uv run bench -l cpp      # only C++ (or -l rust)
uv run bench --native    # optimize for this CPU
```

- **C++** (`bench/cpp/`): [Google Benchmark](https://github.com/google/benchmark), fetched automatically if not installed. Requires CMake (and Ninja, optionally). `--no-build` skips rebuilding.
- **Rust** (`bench/rust/`): [Criterion](https://github.com/bheisler/criterion.rs). Requires Cargo. Criterion compares each run against the previous one automatically.

With a single language, any other arguments go to that language's benchmark tool:

```bash
uv run bench -l cpp serialize --benchmark_filter=Mixed
uv run bench -l rust serialize Mixed
```

To compare C++ changes against a baseline, save results to JSON and diff them with Google Benchmark's `compare.py`:

```bash
uv run bench -l cpp serialize --benchmark_repetitions=10 --benchmark_report_aggregates_only=true --benchmark_out=before.json
```
