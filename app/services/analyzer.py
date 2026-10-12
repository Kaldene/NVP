import os

# Ищем stop_words.txt в корне проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DICT_PATH = os.path.join(BASE_DIR, "stop_words.txt")


def load_dictionary() -> list:
    print("--- ОТЛАДКА СЛОВАРЯ ЗАПУЩЕНА ---")
    print(f"Путь к файлу: {DICT_PATH}")

    if not os.path.exists(DICT_PATH):
        print("Файл stop_words.txt не найден в корне, создаю дефолтный...")
        default_words = ["дурак", "идиот", "блин", "черт", "фигня", "конкурент"]
        with open(DICT_PATH, "w", encoding="utf-8") as f:
            f.write("\n".join(default_words))
        return default_words

    with open(DICT_PATH, "r", encoding="utf-8") as f:
        words = [line.strip().lower() for line in f if line.strip()]
        print(f"Успешно загружено слов: {len(words)} -> {words}")
        return words


STOP_WORDS = load_dictionary()


def analyze_transcript(text: str) -> dict:
    if not text or text.startswith("[Ошибка"):
        return {"tonality": "neutral", "score": 0.0, "violations": []}

    text_lower = text.lower()
    found_violations = []

    for word in STOP_WORDS:
        if word in text_lower:
            found_violations.append({
                "trigger_type": "Стоп-слово",
                "quote": f"Использовано слово: '{word}'"
            })

    if found_violations:
        tonality = "negative"
        score = 20.0
    else:
        tonality = "positive"
        score = 100.0

    return {
        "tonality": tonality,
        "score": score,
        "violations": found_violations
    }