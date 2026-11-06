import re
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from serializer.schema import FieldType, Schemas

TEMPLATE_DIR = Path(__file__).parent / "templates"
SERIALIZE_FILENAME = "serialize"


def pascal_case(value: str) -> str:
    words = re.sub(r"[^a-zA-Z0-9]", " ", value).split()
    return "".join(word.capitalize() for word in words)


# TODO: Make these types real
def cpp_type(t: FieldType) -> str:
    match t:
        case FieldType.I16:
            return "int16_t"
        case FieldType.I32:
            return "int32_t"
        case FieldType.I64:
            return "int64_t"
        case FieldType.I8:
            return "int8_t"
        case FieldType.U8:
            return "uint16_t"
        case FieldType.U16:
            return "uint32_t"
        case FieldType.U64:
            return "int32_t"
        case FieldType.I64:
            return "int64_t"
        case FieldType.F32:
            return "todo"
        case FieldType.F64:
            return "todo"
    raise ValueError(f"Unhandled {t}")


def generate(schemas: Schemas, output: Path) -> None:
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["cpp_type"] = cpp_type

    template = env.get_template(f"{SERIALIZE_FILENAME}.cpp.j2")
    rendered = template.render(schemas=schemas.schemas)

    output.mkdir(parents=True, exist_ok=True)

    output_file = output / "serializer.cpp"
    output_file.write_text(rendered)
