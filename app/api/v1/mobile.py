import os
import shutil
from fastapi import APIRouter, UploadFile, File, Header, HTTPException, Depends, Form
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models import Dialog, Club, Violation, Employee  # <-- Добавили Employee
from app.services.transcription import transcribe_audio
from app.services.analyzer import analyze_transcript

router = APIRouter()


def verify_club_secret(x_club_secret: str = Header(None)):
    if not x_club_secret or x_club_secret != "super_secret_club_123":
        raise HTTPException(status_code=403, detail="Доступ запрещен")
    return x_club_secret


@router.post("/upload")
def upload_audio(
        file: UploadFile = File(...),
        employee_id: int = 1,  # <-- Теперь сервер ждет ID сотрудника
        secret: str = Depends(verify_club_secret),
        db: Session = Depends(get_db)
):
    # Проверяем клуб
    club = db.query(Club).filter(Club.id == 1).first()
    if not club:
        club = Club(id=1, name="MVP Club", secret_key="super_secret_club_123")
        db.add(club)
        db.commit()

    # Проверяем и создаем сотрудника, если его нет (для MVP)
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        employee = Employee(id=employee_id, club_id=1, name=f"Администратор {employee_id}")
        db.add(employee)
        db.commit()

    os.makedirs("uploads", exist_ok=True)
    file_location = f"uploads/{file.filename}"

    with open(file_location, "wb+") as buffer:
        shutil.copyfileobj(file.file, buffer)

    actual_transcript = transcribe_audio(file_location)
    analysis = analyze_transcript(actual_transcript)

    # Сохраняем диалог с привязкой к employee_id
    new_dialog = Dialog(
        club_id=1,
        employee_id=employee_id,  # <-- Привязали!
        audio_file_url=file_location,
        transcript=actual_transcript,
        dialog_type="general",
        tonality=analysis["tonality"],
        score=analysis["score"]
    )
    db.add(new_dialog)
    db.commit()

    for viol in analysis["violations"]:
        new_violation = Violation(dialog_id=new_dialog.id, trigger_type=viol["trigger_type"], quote=viol["quote"])
        db.add(new_violation)

    db.commit()

    return {"status": "success", "transcript": actual_transcript, "employee_id": employee_id}