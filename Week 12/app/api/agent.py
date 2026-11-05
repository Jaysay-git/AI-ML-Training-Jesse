from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.api.dependencies import get_current_user
from app.database.models import User
from app.schemas.agent import AgentQuestion, AgentResponse
from app.agent.agent import ask_naija


router = APIRouter(
    prefix="/agent",
    tags=["AI Agent"],
)


@router.post("/ask", response_model=AgentResponse)
def ask_agent(
    payload: AgentQuestion,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = ask_naija(
        db,
        payload.question,
        user_id=current_user.id,
    )

    return AgentResponse(**result)