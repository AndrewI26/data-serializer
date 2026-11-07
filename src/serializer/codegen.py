import re
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from serializer.schema import Schemas

TEMPLATE_DIR = Path(__file__).parent / "templates"
SERIALIZE_FILENAME = "serialize"


def pascal_case(value: str) -> str:
    words = re.sub(r"[^a-zA-Z0-9]", " ", value).split()
    return "".join(word.capitalize() for word in words)


def generate(schemas: Schemas, output: Path, target: Target) -> None:
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
    )

    template = env.get_template(f"{SERIALIZE_FILENAME}.cpp.j2")
    rendered = template.render(schemas=schemas.schemas)

    output.mkdir(parents=True, exist_ok=True)

    output_file = output / "serializer.cpp"
    output_file.write_text(rendered)
