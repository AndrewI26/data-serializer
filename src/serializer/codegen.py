from enum import Enum
from pathlib import Path
from typing import assert_never

from jinja2 import Environment, FileSystemLoader

from serializer.schema import Schemas

TEMPLATE_DIR = Path(__file__).parent / "templates"


class Target(Enum):
    CPP = "cpp"
    RUST = "rust"

    def file_extension(self) -> str:
        match self:
            case Target.CPP:
                return "hpp"  # header-only: templates must be visible to callers
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
        keep_trailing_newline=True,
    )

    output.mkdir(parents=True, exist_ok=True)

    _generate_types(env, schemas, output, target)

    match mode:
        case UsageMode.SERIALIZATION:
            _generate_serializer(env, schemas, output, target)
        case UsageMode.DESERIALIZE:
            _generate_deserializer(env, schemas, output, target)
        case UsageMode.BOTH:
            _generate_serializer(env, schemas, output, target)
            _generate_deserializer(env, schemas, output, target)
        case _:
            assert_never(mode)


def _generate_types(
    env: Environment, schemas: Schemas, output: Path, target: Target
) -> None:
    """Generates the message type definitions, needed in every mode."""
    ext = target.file_extension()
    _render_to_file(
        env,
        schemas,
        f"{target.folder_name()}/schemas.{ext}.j2",
        output / f"schemas.{ext}",
    )


def _generate_serializer(
    env: Environment, schemas: Schemas, output: Path, target: Target
) -> None:
    ext = target.file_extension()
    _render_to_file(
        env,
        schemas,
        f"{target.folder_name()}/serialize.{ext}.j2",
        output / f"serializer.{ext}",
    )


def _generate_deserializer(
    env: Environment, schemas: Schemas, output: Path, target: Target
) -> None:
    ext = target.file_extension()
    _render_to_file(
        env,
        schemas,
        f"{target.folder_name()}/deserialize.{ext}.j2",
        output / f"deserializer.{ext}",
    )


def _render_to_file(
    env: Environment, schemas: Schemas, template_path: str, output_file: Path
) -> None:
    template = env.get_template(template_path)
    rendered = template.render(schemas=schemas.schemas)
    output_file.write_text(rendered)
