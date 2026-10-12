from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import time

# --- Схемы для авторизации и настроек ---

class MobileAuthRequest(BaseModel):
    secret_key: str # Секретный ключ клуба для подключения телефона[cite: 1]

class ShiftSettings(BaseModel):
    mode: str # "manual" (ручной) или "schedule" (расписание)[cite: 1]
    # Если режим "schedule", передаем расписание (дни недели и время)[cite: 1]
    schedule: Optional[Dict[str, List[str]]] = None

class MobileConfigResponse(BaseModel):
    club_name: str
    # Сколько раз в день синхронизироваться и в какое время (например: 10:00, 14:00, 18:00, 22:00)[cite: 1]
    sync_times: List[time]
    shift_settings: ShiftSettings

# --- Схемы для загрузки файлов и телеметрии ---

class AudioUploadResponse(BaseModel):
    status: str
    file_id: str
    message: str

class MobileStatusReport(BaseModel):
    """
    Периодический отчет от телефона для отображения в админке:
    статус записи, заряд батареи, память и время последней отправки[cite: 1].
    """
    is_recording: bool
    battery_level: int
    storage_used_mb: int
    storage_total_mb: int
    last_sync_time: Optional[str] = None