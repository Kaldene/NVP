from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date, DateTime, JSON, Float, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

# Берем Base ТОЛЬКО из database, не создаем новую!
from app.db.database import Base


class Club(Base):
    __tablename__ = 'clubs'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    secret_key = Column(String, unique=True, nullable=False, index=True)

    blocks = relationship("ScenarioBlock", back_populates="club")
    calendars = relationship("ScenarioCalendar", back_populates="club")
    employees = relationship("Employee", back_populates="club")
    dialogs = relationship("Dialog", back_populates="club")


class ScenarioBlock(Base):
    __tablename__ = 'scenario_blocks'

    id = Column(Integer, primary_key=True, index=True)
    club_id = Column(Integer, ForeignKey('clubs.id'), nullable=False)
    name = Column(String, nullable=False)
    order = Column(Integer, default=0)
    is_required = Column(Boolean, default=True)

    club = relationship("Club", back_populates="blocks")


class ScenarioCalendar(Base):
    __tablename__ = 'scenario_calendars'

    id = Column(Integer, primary_key=True, index=True)
    club_id = Column(Integer, ForeignKey('clubs.id'), nullable=False)
    date_specific = Column(Date, nullable=True, index=True)
    day_of_week = Column(Integer, nullable=True, index=True)
    active_block_ids = Column(JSON, nullable=False)

    club = relationship("Club", back_populates="calendars")


class Employee(Base):
    __tablename__ = 'employees'

    id = Column(Integer, primary_key=True, index=True)
    club_id = Column(Integer, ForeignKey('clubs.id'), nullable=False)
    name = Column(String, nullable=True)
    voice_signature = Column(String, nullable=True)

    club = relationship("Club", back_populates="employees")
    dialogs = relationship("Dialog", back_populates="employee")


class Dialog(Base):
    __tablename__ = "dialogs"

    id = Column(Integer, primary_key=True, index=True)
    club_id = Column(Integer, ForeignKey("clubs.id"), index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=True)

    audio_file_url = Column(String, nullable=True)
    transcript = Column(String, nullable=True)
    dialog_type = Column(String, nullable=True)
    tonality = Column(String, nullable=True)
    negative_reason = Column(String, nullable=True)
    score = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Обратные связи
    club = relationship("Club", back_populates="dialogs")
    employee = relationship("Employee", back_populates="dialogs")

    # ДОБАВЛЕНЫ недостающие связи для нарушений и блоков:
    violations = relationship("Violation", back_populates="dialog")
    completed_blocks = relationship("CompletedBlock", back_populates="dialog")


class Violation(Base):
    __tablename__ = 'violations'

    id = Column(Integer, primary_key=True, index=True)
    dialog_id = Column(Integer, ForeignKey('dialogs.id'), nullable=False)
    trigger_type = Column(String, nullable=False)
    quote = Column(Text, nullable=False)

    dialog = relationship("Dialog", back_populates="violations")


class CompletedBlock(Base):
    __tablename__ = 'completed_blocks'

    id = Column(Integer, primary_key=True, index=True)
    dialog_id = Column(Integer, ForeignKey('dialogs.id'), nullable=False)
    block_id = Column(Integer, ForeignKey('scenario_blocks.id'), nullable=False)
    quote = Column(Text, nullable=False)

    dialog = relationship("Dialog", back_populates="completed_blocks")