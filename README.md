# High Perf Data Serilzation

Data serilization framework for high preformance applications.

Define the shape of your data in a yaml file then use the python library to generate code for serilzation and deserilzation in C++.

## Running the project

```bash
uv sync
uv run schema-serializer examples/simple.yaml
```

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
