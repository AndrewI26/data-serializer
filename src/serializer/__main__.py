import sys

import yaml

HELP_MSG = "Usage: uv run serializer path/to/schema.yaml"


def main():
    try:
        filename = sys.argv[1]
    except IndexError:
        print("Error: Missing input YAML file.", file=sys.stderr)
        print(HELP_MSG, file=sys.stderr)
        sys.exit(1)

    if not filename:
        print("Must pass in filename")

    with open(filename, "r") as file:
        data = yaml.safe_load(file)
        print(data)


if __name__ == "__main__":
    main()
