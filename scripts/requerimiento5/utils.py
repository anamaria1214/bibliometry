import re
from unidecode import unidecode


def extract_field(entry: str, field: str) -> str:
    match = re.search(rf'{field}\s*=\s*{{(.*?)}}', entry, re.IGNORECASE | re.DOTALL)
    if match:
        return match.group(1).strip()
    return ''


def normalize_author_field(authors_raw: str) -> str:
    """Normaliza el campo author: elimina espacios y caracteres"""
    if not authors_raw:
        return ''
    s = unidecode(authors_raw)
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def extract_first_author(authors_raw: str) -> str:
    """Extrae el primer autor de la cadena BibTeX (heurística simple)."""
    if not authors_raw:
        return ''
    s = normalize_author_field(authors_raw)
    # en BibTeX los autores se separan con ' and '
    parts = [p.strip() for p in re.split(r'\s+and\s+', s, flags=re.IGNORECASE) if p.strip()]
    if not parts:
        return ''
    first = parts[0]
    # transformar 'Last, First' a 'First Last'
    if ',' in first:
        pieces = [p.strip() for p in first.split(',')]
        if len(pieces) >= 2:
            first_name = pieces[1] + ' ' + pieces[0]
            return first_name.strip()
    return first
