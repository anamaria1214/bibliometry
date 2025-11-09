import requests
from pathlib import Path
import csv
import time
import re
import pycountry


def _load_cache(cache_path: Path):
    if not cache_path.exists():
        return {}
    d = {}
    with cache_path.open('r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            d[r['doi']] = r['country']
    return d


def _save_cache(cache_path: Path, cache: dict):
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with cache_path.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['doi', 'country'])
        writer.writeheader()
        for doi, country in cache.items():
            writer.writerow({'doi': doi, 'country': country})


def country_from_affiliation_text(text: str):
    if not text:
        return None
    txt = text.lower()
    
    for c in pycountry.countries:
        if c.name.lower() in txt:
            return c.name
        
        if hasattr(c, 'common_name') and c.common_name and c.common_name.lower() in txt:
            return c.name
        
        if hasattr(c, 'official_name') and c.official_name and c.official_name.lower() in txt:
            return c.name

    
    codes = re.findall(r'\b[A-Z]{2}\b', text)
    for code in codes:
        try:
            c = pycountry.countries.get(alpha_2=code.upper())
            if c:
                return c.name
        except Exception:
            pass

    return None


def resolve_country_by_doi(doi: str, cache_path: Path = Path('data/analysis/author_country_cache.csv'), use_crossref: bool = True, sleep_between: float = 1.0):
    """Intenta resolver el país del primer autor usando Crossref (por DOI). Devuelve nombre del país o None.

    Guarda resultados en un CSV cache para evitar llamadas repetidas.
    """
    cache = _load_cache(cache_path)
    if doi in cache:
        return cache[doi]

    country = None
    if use_crossref and doi:
        url = f'https://api.crossref.org/works/{doi}'
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                j = r.json()
                msg = j.get('message', {})
                authors = msg.get('author', [])
                if authors:
                    aff = authors[0].get('affiliation', [])
                    if aff:
                        
                        aff_text = ' '.join(a.get('name', '') for a in aff if a.get('name'))
                        country = country_from_affiliation_text(aff_text)
               
                if not country:
                    
                    raw = str(j)
                    country = country_from_affiliation_text(raw)
        except Exception:
            country = None
        time.sleep(sleep_between)

    
    cache[doi] = country or ''
    _save_cache(cache_path, cache)
    return country
