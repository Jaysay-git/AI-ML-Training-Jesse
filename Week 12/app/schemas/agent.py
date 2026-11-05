from pydantic import BaseModel, Field


class AgentQuestion(BaseModel):
    question: str = Field(min_length=3, max_length=1000)


class AgentResponse(BaseModel):
    answer: str
    tools_used: list[str]
    fallback: bool
