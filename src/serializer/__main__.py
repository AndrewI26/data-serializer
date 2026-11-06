import argparse
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from serializer.schema import Schemas

HELP_MSG = "Usage: uv run serializer path/to/schema.yaml"


class CLIArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    filename: Path
    output: Path = Path("generated")


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

    parsed = parser.parse_args()
    args = CLIArgs.model_validate(vars(parsed))

    data = Schemas.from_yaml(Path(args.filename))
    print(data)


if __name__ == "__main__":
    main()
