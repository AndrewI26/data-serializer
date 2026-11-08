// Runs the Python generator on the shared benchmark schema, writing the Rust
// code into OUT_DIR. Reruns whenever the schema or the generator changes.

use std::env;
use std::path::PathBuf;
use std::process::Command;

fn main() {
    let manifest_dir = PathBuf::from(env::var("CARGO_MANIFEST_DIR").unwrap());
    let repo_root = manifest_dir.join("../..").canonicalize().unwrap();
    let schema = manifest_dir.join("../bench_schemas.yaml");
    let out_dir = env::var("OUT_DIR").unwrap();

    println!("cargo:rerun-if-changed={}", schema.display());
    println!("cargo:rerun-if-changed={}", repo_root.join("src/serializer").display());

    let status = Command::new("uv")
        .arg("run")
        .arg("--project")
        .arg(&repo_root)
        .arg("schema-serializer")
        .arg(&schema)
        .args(["-o", &out_dir, "-t", "rust"])
        .current_dir(&repo_root)
        .status()
        .expect("failed to run `uv`; is it installed and on PATH?");
    assert!(status.success(), "code generation failed");
}
