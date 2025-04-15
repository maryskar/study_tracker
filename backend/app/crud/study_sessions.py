from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import StudySession
from app.schemas import StudySessionCreate

async def create_study_session(db: AsyncSession, user_id: int, session_data: StudySessionCreate):
    now = datetime.utcnow()
    # Если end_time не передан, рассчитываем его на основе duration
    end_time = session_data.end_time or (now + timedelta(minutes=session_data.duration))

    session = StudySession(
        user_id=user_id,
        start_time=now,
        end_time=end_time,
        duration=session_data.duration,
        type=session_data.type
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session
