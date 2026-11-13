from enum import Enum
from pathlib import Path
from typing import Annotated, Any, Literal, Self, assert_never

import yaml
from pydantic import BaseModel, ConfigDict, Discriminator, PositiveInt, Tag


class FieldType:
    @property
    def size(self) -> int:
        raise NotImplementedError

    @property
    def cpp(self) -> str:
        raise NotImplementedError

    @property
    def rust(self) -> str:
        raise NotImplementedError


class FixedType(FieldType, Enum):
    CHAR = "char"
    U8 = "u8"
    U16 = "u16"
    U32 = "u32"
    U64 = "u64"
    I8 = "i8"
    I16 = "i16"
    I32 = "i32"
    I64 = "i64"
    F32 = "f32"
    F64 = "f64"

    @property
    def cpp(self) -> str:
        match self:
            case FixedType.CHAR:
                return "char"
            case FixedType.U8:
                return "uint8_t"
            case FixedType.U16:
                return "uint16_t"
            case FixedType.U32:
                return "uint32_t"
            case FixedType.U64:
                return "uint64_t"
            case FixedType.I8:
                return "int8_t"
            case FixedType.I16:
                return "int16_t"
            case FixedType.I32:
                return "int32_t"
            case FixedType.I64:
                return "int64_t"
            case FixedType.F32:
                return "float"
            case FixedType.F64:
                return "double"
            case _:
                assert_never(self)

    @property
    def rust(self) -> str:
        match self:
            case FixedType.CHAR:
                return "u8"
            case FixedType.U8:
                return "u8"
            case FixedType.U16:
                return "u16"
            case FixedType.U32:
                return "u32"
            case FixedType.U64:
                return "u64"
            case FixedType.I8:
                return "i8"
            case FixedType.I16:
                return "i16"
            case FixedType.I32:
                return "i32"
            case FixedType.I64:
                return "i64"
            case FixedType.F32:
                return "f32"
            case FixedType.F64:
                return "f64"
            case _:
                assert_never(self)

    @property
    def size(self) -> int:
        match self:
            case FixedType.CHAR | FixedType.U8 | FixedType.I8:
                return 1
            case FixedType.U16 | FixedType.I16:
                return 2
            case FixedType.U32 | FixedType.I32 | FixedType.F32:
                return 4
            case FixedType.U64 | FixedType.I64 | FixedType.F64:
                return 8
            case _:
                assert_never(self)


class VariableType(Enum):
    STRING = "string"

    @property
    def element(self) -> FixedType:
        match self:
            case VariableType.STRING:
                return FixedType.CHAR
            case _:
                assert_never(self)


class FixedField(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    type: FixedType

    @property
    def is_variable(self) -> bool:
        return False

    @property
    def total_size(self) -> int:
        return self.type.size

    @property
    def cpp(self) -> str:
        return self.type.cpp

    @property
    def rust(self) -> str:
        return self.type.rust


class VariableField(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    type: VariableType
    size: PositiveInt

    @property
    def is_variable(self) -> bool:
        return True

    @property
    def total_size(self) -> int:
        return self.type.element.size * self.size

    @property
    def cpp(self) -> str:
        return f"{self.type.element.cpp}[{self.size}]"

    @property
    def rust(self) -> str:
        return f"[{self.type.element.rust}; {self.size}]"


_VARIABLE_TYPE_NAMES = {t.value for t in VariableType}


def _field_kind(value: Any) -> Literal["fixed", "variable"]:
    field_type = value.get("type") if isinstance(value, dict) else value.type
    if isinstance(field_type, VariableType) or field_type in _VARIABLE_TYPE_NAMES:
        return "variable"
    return "fixed"


SchemaField = Annotated[
    Annotated[FixedField, Tag("fixed")] | Annotated[VariableField, Tag("variable")],
    Discriminator(_field_kind),
]


class Schema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    fields: list[SchemaField]

    @property
    def size(self) -> int:
        """Size in bytes on the wire (fields are packed, no padding)."""
        return sum(field.total_size for field in self.fields)

    @property
    def layout(self) -> list[tuple[SchemaField, int]]:
        """Each field with its byte offset on the wire."""
        offsets = []
        offset = 0
        for field in self.fields:
            offsets.append((field, offset))
            offset += field.total_size
        return offsets


class Endian(Enum):
    LITTLE = "little"
    BIG = "big"

    @property
    def short(self) -> str:
        match self:
            case Endian.LITTLE:
                return "le"
            case Endian.BIG:
                return "be"
            case _:
                assert_never(self)


class Schemas(BaseModel):
    model_config = ConfigDict(extra="forbid")

    endian: Endian = Endian.LITTLE
    schemas: list[Schema]

    @classmethod
    def from_yaml(cls, path: Path) -> Self:
        with path.open("r") as file:
            data = yaml.safe_load(file)

        return cls.model_validate(data)
