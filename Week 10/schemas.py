
from typing import Any, Literal

from pydantic import BaseModel, Field


class AgentRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)


class ToolCall(BaseModel):
    tool_name: Literal[
        "ask_documents",
        "predict_hospital_risk",
        "lookup_information",
    ]
    arguments: dict[str, Any] = Field(default_factory=dict)


class AgentStep(BaseModel):
    step: int
    tool_name: str
    status: str
    details: str



class DocumentCitation(BaseModel):
    source_id: str
    filename: str
    pages: str
    chunk_index: int


class AgentResponse(BaseModel):
    message: str
    answer: str
    steps: list[AgentStep] = Field(default_factory=list)
    tool_calls: int = 0
    refused: bool = False
    citations: list[DocumentCitation] = Field(default_factory=list)


class HospitalPredictionInput(BaseModel):
    age: int = Field(ge=0, le=120)
    gender: str = Field(min_length=1, max_length=30)
    temperature: float = Field(ge=25, le=45)
    heart_rate: int = Field(ge=0, le=300)
    oxygen_saturation: float = Field(ge=0, le=100)
