"""
ECO COMPANY — Setting Schemas
"""
from pydantic import BaseModel


class SettingUpdate(BaseModel):
    value: str | None = None


class SettingResponse(BaseModel):
    key: str
    value: str | None = None
    type: str = "text"
    label: str | None = None
    is_public: bool = True

    model_config = {"from_attributes": True}
