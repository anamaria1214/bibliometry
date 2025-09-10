import hashlib
import re

def normalize_title(title: str) -> str:
    """
    Normaliza un título eliminando espacios, puntuación y pasándolo a minúsculas
    para detectar duplicados.
    """
    title = title.lower().strip()
    title = re.sub(r'[^a-z0-9 ]', '', title)  # solo letras y números
    return ' '.join(title.split())

def title_hash(title: str) -> str:
    """
    Genera un hash único para cada título normalizado
    """
    return hashlib.md5(normalize_title(title).encode("utf-8")).hexdigest()
