"""Build and run the C++ benchmarks.

Usage:
    uv run bench                    # build, then run every benchmark
    uv run bench serialize          # only serialize/deserialize benchmarks
    uv run bench udp                # only the UDP loopback benchmarks
    uv run bench --native           # optimize for this CPU

Any other arguments are passed through to Google Benchmark, e.g.:
    uv run bench serialize --benchmark_filter=Mixed
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BENCH_DIR = REPO_ROOT / "bench"
CPP_DIR = BENCH_DIR / "cpp"
CPP_BUILD_DIR = CPP_DIR / "build"

BENCHMARKS = {
    "serialize": "serialize_bench",
    "udp": "udp_bench",
}


def run(cmd: list[str]) -> None:
    print(f"$ {' '.join(cmd)}", flush=True)
    subprocess.run(cmd, check=True)


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


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build and run the C++ benchmarks.",
        epilog="Unrecognized arguments are passed to Google Benchmark.",
    )
    parser.add_argument(
        "which",
        nargs="?",
        choices=[*BENCHMARKS, "all"],
        default="all",
        help="Which benchmarks to run (default: all).",
    )
    parser.add_argument(
        "--native",
        action="store_true",
        help="Optimize for this CPU (-march=native).",
    )
    parser.add_argument(
        "--no-build",
        action="store_true",
        help="Skip configuring and building the benchmarks.",
    )
    args, passthrough = parser.parse_known_args()

    if shutil.which("cmake") is None:
        print("error: cmake not found on PATH", file=sys.stderr)
        return 1

    targets = list(BENCHMARKS.values()) if args.which == "all" else [BENCHMARKS[args.which]]

    try:
        run_cpp(targets, args.native, not args.no_build, passthrough)
    except subprocess.CalledProcessError as e:
        return e.returncode

    return 0


if __name__ == "__main__":
    sys.exit(main())
