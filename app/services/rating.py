from typing import List
from app.models import Dialog, ScenarioBlock


def calculate_dialog_score(dialog: Dialog, active_blocks_count: int) -> float:
    """
    Расчет баллов за один конкретный диалог.
    """
    score = 0.0

    # Главный вклад: доля выполненных обязательных блоков[cite: 1]
    # Допустим, каждый выполненный блок дает (100 / active_blocks_count) баллов
    base_block_value = 100.0 / active_blocks_count if active_blocks_count > 0 else 0
    score += len(dialog.completed_blocks) * base_block_value

    # Бонусы: позитивная тональность и сделанная продажа повышают балл[cite: 1]
    if dialog.tonality == "позитив":
        score += 10.0
    if dialog.dialog_type == "продажа":
        score += 15.0

    # Штрафы: негатив и нерешенная проблема понижают балл[cite: 1]
    if dialog.tonality == "негатив":
        score -= 20.0
    if dialog.dialog_type == "проблема":  # если это конфликт/жалоба
        score -= 15.0

    # Найденное нарушение сильно понижает балл за диалог: "грязный" разговор почти ничего не дает[cite: 1]
    if dialog.violations:
        score = min(score, 10.0)  # Жестко срезаем балл

    return max(0.0, min(100.0, score))  # Ограничиваем от 0 до 100


def calculate_daily_rating(dialogs: List[Dialog], active_blocks_count: int) -> float | None:
    """
    Расчет нормализованного рейтинга за день.
    """
    # Считаются только диалоги, где голос сотрудника определён уверенно[cite: 1]
    valid_dialogs = [d for d in dialogs if d.employee_id is not None]

    # Если диалогов меньше 10, рейтинг за день не публикуется (недостаточно данных)[cite: 1]
    if len(valid_dialogs) < 10:
        return None

    scores = [calculate_dialog_score(d, active_blocks_count) for d in valid_dialogs]

    # Берётся усреднённое без крайних выбросов (чтобы один конфликт или идеальный разговор не исказили картину)[cite: 1]
    if len(scores) >= 10:
        scores.sort()
        # Отбрасываем 10% лучших и 10% худших диалогов
        trim_count = max(1, len(scores) // 10)
        scores = scores[trim_count:-trim_count]

    average_score = sum(scores) / len(scores) if scores else 0.0
    return round(average_score, 2)