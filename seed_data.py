import random
from datetime import datetime, timedelta
from app.db.database import SessionLocal, engine
from app.models import Base, Club, Employee, Dialog, Violation


def seed_database():
    db = SessionLocal()

    # 1. Создаем клуб
    club = db.query(Club).filter(Club.id == 1).first()
    if not club:
        club = Club(id=1, name="MVP Club", secret_key="super_secret_club_123")
        db.add(club)
        db.commit()

    # 2. Создаем сотрудников
    employees = [
        {"id": 1, "name": "Анна (Хороший админ)"},
        {"id": 2, "name": "Иван (Стажер)"}
    ]
    for emp_data in employees:
        emp = db.query(Employee).filter(Employee.id == emp_data["id"]).first()
        if not emp:
            emp = Employee(id=emp_data["id"], club_id=1, name=emp_data["name"])
            db.add(emp)
    db.commit()

    # 3. Генерируем диалоги
    today = datetime.now()
    yesterday = today - timedelta(days=1)

    templates = [
        # Успешные продажи (Анна)
        {"emp_id": 1,
         "text": "Здравствуйте! Добро пожаловать. Будете брать пакет на 3 часа или на ночь? Могу предложить энергетик.",
         "tonality": "positive", "score": 100, "violations": []},
        {"emp_id": 1, "text": "Да, конечно, сейчас пересажу вас за VIP компьютер. Приятной игры!",
         "tonality": "positive", "score": 100, "violations": []},

        # Нарушения (Иван)
        {"emp_id": 2, "text": "Слушай, блин, у нас компы зависают, это фигня какая-то. Иди лучше в colizeum играй.",
         "tonality": "negative", "score": 10, "violations": ["блин", "фигня", "colizeum"]},
        {"emp_id": 2, "text": "Переведи мне на карту мимо кассы, я тебе скидку сделаю.", "tonality": "negative",
         "score": 0, "violations": ["мимо кассы", "на карту"]},

        # Нейтральные (Оба)
        {"emp_id": 1, "text": "Ваше время вышло, будете продлевать?", "tonality": "positive", "score": 80,
         "violations": []},
        {"emp_id": 2, "text": "Не знаю, сам виноват, что наушники не работают.", "tonality": "negative", "score": 20,
         "violations": ["сам виноват", "не знаю"]}
    ]

    for _ in range(15):  # Создаем 15 случайных диалогов
        template = random.choice(templates)
        # Случайно разбрасываем по времени: сегодня или вчера
        created_time = today if random.random() > 0.3 else yesterday
        created_time = created_time.replace(hour=random.randint(10, 22), minute=random.randint(0, 59))

        dialog = Dialog(
            club_id=1,
            employee_id=template["emp_id"],
            audio_file_url="",  # Пустая ссылка, чтобы плеер не ломался без реального файла
            transcript=template["text"],
            dialog_type="general",
            tonality=template["tonality"],
            score=template["score"]
        )
        dialog.created_at = created_time
        db.add(dialog)
        db.commit()
        db.refresh(dialog)

        # Добавляем нарушения
        for viol in template["violations"]:
            violation = Violation(dialog_id=dialog.id, trigger_type="Стоп-слово", quote=f"Слово: {viol}")
            db.add(violation)
        db.commit()

    print("✅ База данных успешно заполнена тестовыми данными для презентации!")
    db.close()


if __name__ == "__main__":
    seed_database()