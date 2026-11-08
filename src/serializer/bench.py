"""Build and run the C++ and Rust benchmarks.

Usage:
    uv run bench                    # build, then run every benchmark in both languages
    uv run bench serialize          # only serialize/deserialize benchmarks
    uv run bench udp                # only the UDP loopback benchmarks
    uv run bench -l cpp             # only C++ (or -l rust)
    uv run bench --native           # optimize for this CPU

With a single language, any other arguments are passed through to that
language's benchmark tool (Google Benchmark for C++, Criterion for Rust), e.g.:
    uv run bench -l cpp serialize --benchmark_filter=Mixed
    uv run bench -l rust serialize Mixed
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BENCH_DIR = REPO_ROOT / "bench"
CPP_DIR = BENCH_DIR / "cpp"
CPP_BUILD_DIR = CPP_DIR / "build"
RUST_MANIFEST = BENCH_DIR / "rust" / "Cargo.toml"

# Benchmark set -> executable (C++) / bench target (Rust). Same names in both.
BENCHMARKS = {
    "serialize": "serialize_bench",
    "udp": "udp_bench",
}
LANGUAGES = ("cpp", "rust")
REQUIRED_TOOL = {"cpp": "cmake", "rust": "cargo"}


def run(cmd: list[str], env: dict[str, str] | None = None) -> None:
    print(f"$ {' '.join(cmd)}", flush=True)
    subprocess.run(cmd, check=True, env=env)


def build_cpp(native: bool) -> None:
    configure = [
        "cmake",
        "-S",
        str(CPP_DIR),
        "-B",
        str(CPP_BUILD_DIR),
        f"-DBENCH_NATIVE={'ON' if native else 'OFF'}",
    ]
    # The generator can only be chosen on the first configure.
    if not (CPP_BUILD_DIR / "CMakeCache.txt").exists() and shutil.which("ninja"):
        configure += ["-G", "Ninja"]
    run(configure)
    run(["cmake", "--build", str(CPP_BUILD_DIR)])


def run_cpp(targets: list[str], native: bool, build: bool, passthrough: list[str]) -> None:
    if build:
        build_cpp(native)
    for target in targets:
        exe = CPP_BUILD_DIR / target
        if not exe.exists():
            raise SystemExit(f"error: {exe} not found; run without --no-build first")
        run([str(exe), *passthrough])


def run_rust(targets: list[str], native: bool, passthrough: list[str]) -> None:
    env = os.environ.copy()
    if native:
        env["RUSTFLAGS"] = f"{env.get('RUSTFLAGS', '')} -C target-cpu=native".strip()
    # `cargo bench` always (incrementally) rebuilds, so --no-build doesn't apply.
    for target in targets:
        cmd = ["cargo", "bench", "--manifest-path", str(RUST_MANIFEST), "--bench", target]
        if passthrough:
            cmd += ["--", *passthrough]
        run(cmd, env=env)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build and run the C++ and Rust benchmarks.",
        epilog="With a single --lang, unrecognized arguments are passed to that "
        "language's benchmark tool.",
    )
    parser.add_argument(
        "which",
        nargs="?",
        choices=[*BENCHMARKS, "all"],
        default="all",
        help="Which benchmarks to run (default: all).",
    )
    parser.add_argument(
        "-l",
        "--lang",
        choices=[*LANGUAGES, "all"],
        default="all",
        help="Which language's benchmarks to run (default: all).",
    )
    parser.add_argument(
        "--native",
        action="store_true",
        help="Optimize for this CPU (-march=native / -C target-cpu=native).",
    )
    parser.add_argument(
        "--no-build",
        action="store_true",
        help="Skip configuring and building the C++ benchmarks.",
    )
    args, passthrough = parser.parse_known_args()

    languages = list(LANGUAGES) if args.lang == "all" else [args.lang]
    if passthrough and len(languages) > 1:
        parser.error(
            f"extra arguments {passthrough} need a single language (-l cpp or -l rust), "
            "since C++ and Rust use different benchmark tools"
        )

    for lang in languages:
        tool = REQUIRED_TOOL[lang]
        if shutil.which(tool) is None:
            print(f"error: {tool} not found on PATH (needed for {lang})", file=sys.stderr)
            return 1

    targets = list(BENCHMARKS.values()) if args.which == "all" else [BENCHMARKS[args.which]]

    try:
        for lang in languages:
            print(f"\n=== {lang} ===", flush=True)
            if lang == "cpp":
                run_cpp(targets, args.native, not args.no_build, passthrough)
            else:
                run_rust(targets, args.native, passthrough)
    except subprocess.CalledProcessError as e:
        return e.returncode

    return 0


if __name__ == "__main__":
    sys.exit(main())
