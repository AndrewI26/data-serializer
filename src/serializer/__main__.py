import argparse
from enum import Enum
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from serializer.codegen import generate
from serializer.schema import Schemas

HELP_MSG = "Usage: uv run serializer path/to/schema.yaml"


class UsageMode(Enum):
    SERIALIZATION = "serialize"
    DESERIALIZE = "deserialize"
    BOTH = "both"


class Target(Enum):
    CPP = "cpp"
    RUST = "rust"


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
        "-m",
        "--mode",
        type=UsageMode,
        choices=[mode for mode in UsageMode if mode != UsageMode.BOTH],
        default=UsageMode.BOTH,
        help="Specifies which type of code to generate.",
    )
    parser.add_argument(
        "-t",
        "--target",
        type=Target,
        choices=Target,
        help="Target for generated code.",
    )

    parsed = parser.parse_args()
    args = CLIArgs.model_validate(vars(parsed))

    data = Schemas.from_yaml(Path(args.filename))

    generate(data, args.output)


if __name__ == "__main__":
    main()
