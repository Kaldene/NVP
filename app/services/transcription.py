import os
import wave
import json
from vosk import Model, KaldiRecognizer

# Указываем базовый путь
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "model")

# Умный поиск: если при распаковке создалась подпапка, указываем путь к ней
NESTED_MODEL_PATH = os.path.join(MODEL_PATH, "vosk-model-small-ru-0.22")
if os.path.exists(NESTED_MODEL_PATH):
    MODEL_PATH = NESTED_MODEL_PATH

# Безопасная загрузка модели (чтобы сервер не падал при ошибке)
try:
    # Проверяем, есть ли по итоговому пути нужные файлы (например, папка am)
    if os.path.exists(os.path.join(MODEL_PATH, "am")):
        model = Model(MODEL_PATH)
    else:
        model = None
        print(f"ВНИМАНИЕ: Файлы модели не найдены внутри {MODEL_PATH}")
except Exception as e:
    model = None
    print(f"ВНИМАНИЕ: Ошибка инициализации Vosk: {e}")


def transcribe_audio(file_path: str) -> str:
    if not model:
        return "[Ошибка: Модель Vosk не загружена. Проверьте папку model]"

    try:
        wf = wave.open(file_path, "rb")

        if wf.getnchannels() != 1:
            return "[Ошибка: Файл должен быть монофоническим]"

        rec = KaldiRecognizer(model, wf.getframerate())
        rec.SetWords(True)

        results = []
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                part_result = json.loads(rec.Result())
                results.append(part_result.get("text", ""))

        final_result = json.loads(rec.FinalResult())
        results.append(final_result.get("text", ""))

        transcript = " ".join(filter(None, results)).strip()
        return transcript if transcript else "[Речь не распознана]"

    except Exception as e:
        return f"[Ошибка обработки файла: {str(e)}]"