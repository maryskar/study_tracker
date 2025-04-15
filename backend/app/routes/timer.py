from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import get_db
from app.models.models import StudySession
from app.schemas.timer import *
from datetime import datetime
from app.crud.auth import get_current_user

router = APIRouter(prefix="/api/timer", tags=["Timer"])

@router.post("/start", response_model=TimerStartResponse)
async def start_timer(
    data: TimerStartRequest,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    new_session = StudySession(
        user_id=user.id,
        start_time=datetime.utcnow(),
        end_time=None,
        duration=data.duration,
        type=data.type,
    )
    db.add(new_session)
    await db.commit()
    await db.refresh(new_session)
    return {"sessionId": new_session.id, "status": "running"}


@router.post("/stop", response_model=TimerStopResponse)
async def stop_timer(
    data: TimerStopRequest,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    session = await db.get(StudySession, data.sessionId)
    if not session or session.user_id != user.id:
        raise HTTPException(status_code=404, detail="Session not found")

    session.status = "stopped"
    session.end_time = datetime.utcnow()
    await db.commit()

    time_spent = (session.end_time - session.start_time).seconds // 60
    return {"status": "stopped", "timeSpent": time_spent}

@router.get("/status", response_model=TimerStatusResponse)
async def timer_status(
    sessionId: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    session = await db.get(StudySession, sessionId)
    if not session or session.user_id != user.id:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.status == "stopped":
        remaining = 0
    else:
        elapsed = (datetime.utcnow() - session.start_time).seconds // 60
        remaining = max(session.duration - elapsed, 0)

    return {"status": session.status, "remainingTime": remaining}
