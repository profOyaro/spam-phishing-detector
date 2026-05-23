"""Pydantic schemas for the FastAPI backend."""
from pydantic import BaseModel, Field

class AnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=200000)
    sender: str = Field(default="", max_length=320)
    subject: str = Field(default="", max_length=500)

class UrlRequest(BaseModel):
    url: str = Field(..., min_length=5, max_length=2048)
