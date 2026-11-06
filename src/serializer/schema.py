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


class Field(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    type: FieldType


class Schema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    fields: list[Field]


class Schemas(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schemas: list[Schema]

    @classmethod
    def from_yaml(cls, path: Path) -> Self:
        with path.open("r") as file:
            data = yaml.safe_load(file)

        return cls.model_validate(data)
