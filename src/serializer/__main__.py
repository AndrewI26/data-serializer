import argparse
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from serializer.codegen import Target, UsageMode, generate
from serializer.schema import Schemas


class CLIArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    filename: Path
    output: Path = Path("generated")
    mode: UsageMode = UsageMode.BOTH
    target: Target


def main():
    parser = argparse.ArgumentParser(
        prog="bin-serializer",
        description="Generate binary (de)serializer from YAML schemas.",
    )
    parser.add_argument("filename", type=Path, help="Path to the YAML schema file.")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("generated"),
        help="Directory for generated code.",
    )
    parser.add_argument(
        "-t",
        "--target",
        type=Target,
        choices=Target,
        default=Target.CPP,
        help="Target for generated code.",
    )
    parser.add_argument(
        "-m",
        "--mode",
        type=UsageMode,
        choices=[mode for mode in UsageMode if mode != UsageMode.BOTH],
        default=UsageMode.BOTH,
        help="Specifies which type of code to generate.",
    )

    parsed = parser.parse_args()
    args = CLIArgs.model_validate(vars(parsed))

    data = Schemas.from_yaml(Path(args.filename))

    generate(data, args.output, args.target, args.mode)


if __name__ == "__main__":
    main()
