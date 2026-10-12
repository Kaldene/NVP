from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date
from app.db.database import get_db
from app.models import Dialog, Employee  # <-- Добавили Employee
from pydantic import BaseModel
from fastapi import HTTPException
router = APIRouter()


# Новый эндпоинт: отдает список всех администраторов клуба
@router.get("/employees")
def get_employees(club_id: int = 1, db: Session = Depends(get_db)):
    employees = db.query(Employee).filter(Employee.club_id == club_id).all()
    return [{"id": e.id, "name": e.name} for e in employees]


@router.get("/summary")
def get_daily_summary(target_date: date, club_id: int = 1, employee_id: int = None, db: Session = Depends(get_db)):
    query = db.query(Dialog).filter(Dialog.club_id == club_id, func.date(Dialog.created_at) == target_date)

    if employee_id:  # Если запросили конкретного админа - фильтруем
        query = query.filter(Dialog.employee_id == employee_id)

    dialogs = query.all()
    total_dialogs = len(dialogs)
    negative_dialogs = sum(1 for d in dialogs if d.tonality == "negative")
    negative_share = round((negative_dialogs / total_dialogs) * 100) if total_dialogs > 0 else 0

    return {"total_dialogs": total_dialogs, "negative_share_percent": negative_share}


@router.get("/dialogs")
def get_dialogs(target_date: date = None, club_id: int = 1, employee_id: int = None, db: Session = Depends(get_db)):
    query = db.query(Dialog).filter(Dialog.club_id == club_id)
    if target_date:
        query = query.filter(func.date(Dialog.created_at) == target_date)
    if employee_id:
        query = query.filter(Dialog.employee_id == employee_id)

    dialogs = query.order_by(Dialog.id.desc()).limit(50).all()

    result = []
    for d in dialogs:
        # Достаем имя сотрудника для таблицы
        emp_name = d.employee.name if d.employee else f"ID {d.employee_id}"
        result.append({
            "id": d.id,
            "employee": emp_name,
            "time": d.created_at.strftime("%H:%M:%S") if d.created_at else "",
            "transcript": d.transcript or "Нет текста",
            "tonality": d.tonality,
            "violations": [v.trigger_type for v in d.violations],
            "audio_url": f"http://127.0.0.1:8000/{d.audio_file_url}" if d.audio_file_url else None
        })
    return result


class EmployeeCreate(BaseModel):
    name: str


@router.post("/employees")
def create_employee(emp: EmployeeCreate, club_id: int = 1, db: Session = Depends(get_db)):
    new_emp = Employee(club_id=club_id, name=emp.name)
    db.add(new_emp)
    db.commit()
    db.refresh(new_emp)
    return {"status": "success", "id": new_emp.id, "name": new_emp.name}


@router.delete("/employees/{employee_id}")
def delete_employee(employee_id: int, club_id: int = 1, db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(Employee.id == employee_id, Employee.club_id == club_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")

    db.delete(emp)
    db.commit()
    return {"status": "success"}