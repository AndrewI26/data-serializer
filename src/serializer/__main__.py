import sys

import yaml

from serializer.schema import Schemas

HELP_MSG = "Usage: uv run serializer path/to/schema.yaml"


def parse_schema(path: str) -> Schemas:
    with open(path, "r") as file:
        data = yaml.safe_load(file)

    return Schemas.model_validate(data)


def main():
    try:
        filename = sys.argv[1]
    except IndexError:
        print("Error: Missing input YAML file.", file=sys.stderr)
        print(HELP_MSG, file=sys.stderr)
        sys.exit(1)

    if not filename:
        print("Must pass in filename")

    data = parse_schema(filename)

    print(data)


if __name__ == "__main__":
    main()
