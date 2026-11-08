from enum import Enum
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from serializer.schema import Schemas

TEMPLATE_DIR = Path(__file__).parent / "templates"


class Target(Enum):
    CPP = "cpp"
    RUST = "rust"

    def file_extension(self) -> str:
        match self:
            case Target.CPP:
                return "cpp"
            case Target.RUST:
                return "rs"

    def folder_name(self) -> str:
        match self:
            case Target.CPP:
                return "cpp"
            case Target.RUST:
                return "rust"


class UsageMode(Enum):
    SERIALIZATION = "serialize"
    DESERIALIZE = "deserialize"
    BOTH = "both"


def generate(schemas: Schemas, output: Path, target: Target, mode: UsageMode) -> None:
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
    )

    match mode:
        case UsageMode.SERIALIZATION:
            template = env.get_template(
                f"{target.folder_name()}/serialize.{target.file_extension()}.j2"
            )
            rendered = template.render(schemas=schemas.schemas)

            output.mkdir(parents=True, exist_ok=True)

            output_file = output / f"serializer.{target.file_extension}"
            output_file.write_text(rendered)
        case UsageMode.DESERIALIZE:
            template = env.get_template(
                f"{target.folder_name()}/deserialize.{target.file_extension()}.j2"
            )
            rendered = template.render(schemas=schemas.schemas)

            output.mkdir(parents=True, exist_ok=True)

            output_file = output / f"deserializer.{target.file_extension()}"
            output_file.write_text(rendered)
