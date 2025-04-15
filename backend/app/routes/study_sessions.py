from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import get_db
from app.schemas.timer import StudySessionCreate, StudySessionOut
from app.crud import study_sessions
from app.crud.auth import get_current_user

router = APIRouter()

@router.post("/", response_model=StudySessionOut)
async def create_session(
    session_data: StudySessionCreate,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user),
):
    return await study_sessions.create_study_session(db, user_id=user.id, session_data=session_data)
