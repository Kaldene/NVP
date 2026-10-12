import hashlib

def verify_pin(plain_pin: str, hashed_pin: str) -> bool:
    """
    Проверяет введенный администратором PIN-код[cite: 1].
    В MVP используем базовое хеширование SHA-256.
    """
    return hashlib.sha256(plain_pin.encode()).hexdigest() == hashed_pin

def get_pin_hash(pin: str) -> str:
    """
    Хеширует PIN-код при его создании или изменении в админке.
    """
    return hashlib.sha256(pin.encode()).hexdigest()