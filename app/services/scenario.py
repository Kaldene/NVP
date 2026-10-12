from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from datetime import date
from typing import List

from app.models import ScenarioCalendar, ScenarioBlock


def get_active_blocks_for_date(db: Session, club_id: int, target_date: date) -> List[int]:
    """
    Возвращает список ID блоков сценария, которые должны использоваться в конкретную дату.
    Календарь сценария позволяет задать свой набор блоков на день недели или конкретную дату.
    """
    # 0 = Понедельник, 6 = Воскресенье (соответствует встроенному методу weekday() в Python)
    target_dow = target_date.weekday()

    # Ищем все подходящие правила для клуба, используя логику приоритетов
    calendar_rule = db.query(ScenarioCalendar).filter(
        ScenarioCalendar.club_id == club_id,
        or_(
            # Приоритет 1: Конкретная дата[cite: 1]
            ScenarioCalendar.date_specific == target_date,

            # Приоритет 2: День недели[cite: 1]
            and_(
                ScenarioCalendar.date_specific == None,
                ScenarioCalendar.day_of_week == target_dow
            )
        )
    ).order_by(
        # Сортируем так, чтобы правило с конкретной датой всегда оказывалось первым (высший приоритет)[cite: 1]
        ScenarioCalendar.date_specific.isnot(None).desc(),
        ScenarioCalendar.day_of_week.isnot(None).desc()
    ).first()

    # Если найдено специфичное правило, возвращаем его набор блоков
    if calendar_rule and calendar_rule.active_block_ids:
        return calendar_rule.active_block_ids

    # Если на этот день нет особых правил, возвращаем стартовый (общий) набор блоков клуба[cite: 1]
    default_blocks = db.query(ScenarioBlock).filter(
        ScenarioBlock.club_id == club_id
    ).order_by(
        ScenarioBlock.order  # У каждого блока есть свой порядок[cite: 1]
    ).all()

    return [block.id for block in default_blocks]


def get_scenario_details(db: Session, club_id: int, block_ids: List[int]) -> List[ScenarioBlock]:
    """
    Вспомогательная функция для получения полных объектов блоков по их ID,
    чтобы ML-воркер знал, какие именно фразы (приветствие, предложить еду и т.д.) искать в тексте[cite: 1].
    """
    blocks = db.query(ScenarioBlock).filter(
        ScenarioBlock.id.in_(block_ids),
        ScenarioBlock.club_id == club_id
    ).all()

    # Сортируем в том же порядке, в котором они были переданы
    block_map = {block.id: block for block in blocks}
    return [block_map[b_id] for b_id in block_ids if b_id in block_map]