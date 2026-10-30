"""
ECO COMPANY — Setting Schemas
"""
from pydantic import BaseModel, Field, field_validator


class SettingBulkUpdate(BaseModel):
    key: str = Field(..., min_length=1, max_length=100)
    value: str | None = Field(default=None, max_length=10000)

    @field_validator("key")
    @classmethod
    def trim_key(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Sozlama kaliti bo'sh bo'lmasligi kerak")
        return value


class SettingUpdate(BaseModel):
    value: str | None = Field(default=None, max_length=10000)


class SettingResponse(BaseModel):
    key: str
    value: str | None = None
    type: str = "text"
    label: str | None = None
    is_public: bool = True

    model_config = {"from_attributes": True}
