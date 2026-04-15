import re
from transliterate import translit


# Словарь бизнес-сокращений (можешь расширять)
WORD_MAP = {
    "medicinskii": "MED",
    "meditsinskii": "MED",
    "med": "MED",

    "finansy": "FIN",
    "finansovyi": "FIN",
    "finance": "FIN",

    "razrabotka": "DEV",
    "development": "DEV",
    "dev": "DEV",

    "administrativnyi": "ADMIN",
    "administrativnye": "ADMIN",
    "admin": "ADMIN",

    "marketing": "MKT",
    "prodazhi": "SALES",
    "logistika": "LOG",
    "proekt": "PRJ",
}


STOP_WORDS = {
    "i", "and", "po", "dlya", "the",
    "napravlenie", "kompaniya", "otdel", "gruppa"
}


def normalize_text(text: str) -> str:
    text = translit(text, "ru", reversed=True)
    text = text.lower()
    text = text.replace("-", " ")
    text = re.sub(r"[^a-z0-9\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def build_base_code(name: str) -> str:
    normalized = normalize_text(name)
    words = normalized.split()

    # 1. ищем в словаре
    for word in words:
        if word in WORD_MAP:
            return WORD_MAP[word]

    # 2. убираем стоп-слова
    meaningful = [w for w in words if w not in STOP_WORDS]

    # 3. если несколько слов → инициалы
    if len(meaningful) >= 2:
        return "".join(w[0] for w in meaningful[:4]).upper()

    # 4. если одно слово → первые буквы
    if len(meaningful) == 1:
        return meaningful[0][:6].upper()

    # 5. fallback
    if words:
        return words[0][:6].upper()

    return "CODE"


def generate_unique_code(model_class, name: str, instance_pk=None) -> str:
    base_code = build_base_code(name)
    candidate = base_code
    counter = 2

    while model_class.objects.filter(code=candidate).exclude(pk=instance_pk).exists():
        candidate = f"{base_code}_{counter}"
        counter += 1

    return candidate