"""
ECO COMPANY — Instagram Schemas
"""
from pydantic import BaseModel


class InstagramVideoLinkInput(BaseModel):
    url: str


class InstagramLinksUpdate(BaseModel):
    items: list[InstagramVideoLinkInput]


class InstagramVideoLinkResponse(BaseModel):
    id: str
    url: str
    permalink: str
    embed_url: str
    media_type: str = "VIDEO"
    kind: str


class InstagramStatusResponse(BaseModel):
    mode: str = "manual"
    is_configured: bool
    link_count: int
    message: str
