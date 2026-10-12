from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import date, datetime


# --- Схемы для управления клубом и сценариями ---

class ScenarioBlockBase(BaseModel):
    name: str  # Название, например: "Предложить напиток"
    order: int
    is_required: bool  # Отметка «обязательный» или «необязательный»


class ScenarioBlockCreate(ScenarioBlockBase):
    pass


class ScenarioBlockResponse(ScenarioBlockBase):
    id: int
    club_id: int

    class Config:
        from_attributes = True


# --- Схемы для сотрудников и голосов ---

class EmployeeResponse(BaseModel):
    id: int
    name: Optional[str]  # Имя, которое администратор назначает распознанному голосу[cite: 1]
    voice_signature_id: str

    class Config:
        from_attributes = True


# --- Схемы для аналитики и диалогов ---

class ViolationResponse(BaseModel):
    trigger_type: str  # грубость, оплата мимо кассы и т.д.[cite: 1]
    quote: str  # Цитата нарушения[cite: 1]


class CompletedBlockResponse(BaseModel):
    block_id: int
    quote: str  # Цитата выполнения блока[cite: 1]


class DialogCardResponse(BaseModel):
    id: int
    employee_name: Optional[str]
    dialog_type: str  # новый клиент, пополнение, продление и т.д.[cite: 1]
    tonality: str  # позитив, нейтрально, негатив[cite: 1]
    score: Optional[float]
    violations: List[ViolationResponse]
    completed_blocks: List[CompletedBlockResponse]
    created_at: datetime

    # Текст с раздельной раскраской клиента и сотрудника (передаем как массив реплик)[cite: 1]
    transcript_data: List[Dict[str, str]]

    class Config:
        from_attributes = True


# --- Схемы для рейтингов ---

class EmployeeRatingDay(BaseModel):
    employee_id: int
    employee_name: Optional[str]
    date: date
    score: float  # Рейтинг за день от 0 до 100[cite: 1]
    dialogs_count: int
    # Разбивка: блоки / тональность / продажи[cite: 1]
    breakdown: Dict[str, float]