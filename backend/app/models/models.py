from sqlalchemy import Column, Integer, String, Text, ForeignKey, TIMESTAMP, Boolean, CheckConstraint, Interval, UniqueConstraint, func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# 1. User
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(Text, unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    google_id = Column(Text, unique=True, nullable=True)

    study_sessions = relationship("StudySession", back_populates="user")
    timers = relationship("Timer", back_populates="user")
    stopwatches = relationship("Stopwatch", back_populates="user")
    rewards = relationship("UserReward", back_populates="user")
    settings = relationship("UserSettings", back_populates="user", uselist=False)

# 2. StudySession
class StudySession(Base):
    __tablename__ = "study_sessions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    start_time = Column(TIMESTAMP, nullable=False)
    end_time = Column(TIMESTAMP, nullable=False)
    duration = Column(Integer, nullable=False)
    type = Column(String, nullable=False)

    __table_args__ = (
        CheckConstraint("type IN ('pomodoro', 'stopwatch')", name="study_type_check"),
    )

    user = relationship("User", back_populates="study_sessions")

# 3. Timer
class Timer(Base):
    __tablename__ = "timers"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    duration = Column(Integer, nullable=False)
    status = Column(String, nullable=False)
    remaining_time = Column(Integer, nullable=True)

    __table_args__ = (
        CheckConstraint("status IN ('running', 'paused', 'stopped')", name="timer_status_check"),
    )

    user = relationship("User", back_populates="timers")

# 4. Stopwatch
class Stopwatch(Base):
    __tablename__ = "stopwatches"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    start_time = Column(TIMESTAMP, nullable=False)
    end_time = Column(TIMESTAMP, nullable=True)
    duration = Column(Interval, nullable=True)

    user = relationship("User", back_populates="stopwatches")

# 5. Reward
class Reward(Base):
    __tablename__ = "rewards"

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    description = Column(Text)
    threshold_minutes = Column(Integer, nullable=False)

    users = relationship("UserReward", back_populates="reward")

# 6. UserReward
class UserReward(Base):
    __tablename__ = "user_rewards"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reward_id = Column(Integer, ForeignKey("rewards.id"), nullable=False)
    achieved_at = Column(TIMESTAMP, server_default=func.now())

    user = relationship("User", back_populates="rewards")
    reward = relationship("Reward", back_populates="users")

# 7. UserSettings
class UserSettings(Base):
    __tablename__ = "user_settings"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    theme = Column(String, default='light')
    language = Column(String, default='en')
    notifications = Column(Boolean, default=True)

    __table_args__ = (
        CheckConstraint("theme IN ('light', 'dark')", name="theme_check"),
    )

    user = relationship("User", back_populates="settings")