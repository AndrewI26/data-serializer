from enum import Enum
from pathlib import Path
from typing import Self

import yaml
from pydantic import BaseModel, ConfigDict


class FieldType(str, Enum):
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
        return _CPP_TYPE[self]

    @property
    def rust(self) -> str:
        return _RUST_TYPE[self]

    @property
    def size(self) -> int:
        return _SIZE[self]


_CPP_TYPE = {
    FieldType.U8: "uint8_t",
    FieldType.U16: "uint16_t",
    FieldType.U32: "uint32_t",
    FieldType.U64: "uint64_t",
    FieldType.I8: "int8_t",
    FieldType.I16: "int16_t",
    FieldType.I32: "int32_t",
    FieldType.I64: "int64_t",
    FieldType.F32: "float",
    FieldType.F64: "double",
}


_RUST_TYPE = {
    FieldType.U8: "u8",
    FieldType.U16: "u16",
    FieldType.U32: "u32",
    FieldType.U64: "u64",
    FieldType.I8: "i8",
    FieldType.I16: "i16",
    FieldType.I32: "i32",
    FieldType.I64: "i64",
    FieldType.F32: "f32",
    FieldType.F64: "f64",
}


_SIZE = {
    FieldType.U8: 1,
    FieldType.I8: 1,
    FieldType.U16: 2,
    FieldType.I16: 2,
    FieldType.U32: 4,
    FieldType.I32: 4,
    FieldType.F32: 4,
    FieldType.U64: 8,
    FieldType.I64: 8,
    FieldType.F64: 8,
}

assert set(_CPP_TYPE) == set(_RUST_TYPE) == set(_SIZE) == set(FieldType)


class Field(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    type: FieldType


class Schema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    fields: list[Field]

    @property
    def size(self) -> int:
        """Size in bytes on the wire (fields are packed, no padding)."""
        return sum(field.type.size for field in self.fields)


class Schemas(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schemas: list[Schema]

    @classmethod
    def from_yaml(cls, path: Path) -> Self:
        with path.open("r") as file:
            data = yaml.safe_load(file)

        return cls.model_validate(data)
