import re
from pathlib import Path
import pandas as pd
from .utils import extract_field, normalize_author_field, extract_first_author


def parse_bib_file(bib_path: Path) -> pd.DataFrame:
    """Parsea un archivo .bib y retorna un DataFrame con campos clave.

    Campos retornados: doi, title, authors_raw, first_author, year, journal, abstract, keywords
    """
    text = bib_path.read_text(encoding='utf-8', errors='ignore')
    raw_entries = re.findall(r'@\w+\s*{[^@]*}', text, re.DOTALL)

    rows = []
    for entry in raw_entries:
        doi = extract_field(entry, 'doi')
        title = extract_field(entry, 'title')
        authors_raw = extract_field(entry, 'author')
        year = extract_field(entry, 'year')
        
        journal = extract_field(entry, 'journal') or extract_field(entry, 'booktitle')
        abstract = extract_field(entry, 'abstract')
        keywords = extract_field(entry, 'keywords')

        first_author = extract_first_author(authors_raw)

        rows.append({
            'doi': doi.strip(),
            'title': title.strip(),
            'authors_raw': authors_raw.strip(),
            'first_author': first_author,
            'year': year.strip(),
            'journal': journal.strip(),
            'abstract': abstract.strip(),
            'keywords': keywords.strip(),
        })

    df = pd.DataFrame(rows)
    
    df['year'] = pd.to_numeric(df['year'], errors='coerce').astype('Int64')
    df['text_for_wordcloud'] = (df['abstract'].fillna('') + ' ' + df['keywords'].fillna('')).str.strip()

    return df


def save_metadata(df: pd.DataFrame, out_csv: Path):
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_csv, index=False, encoding='utf-8')


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Parse .bib into a metadata CSV')
    parser.add_argument('-i', '--input', required=True, help='Path to unified_references.bib')
    parser.add_argument('-o', '--output', default='data/analysis/metadata.csv', help='Output CSV path')
    args = parser.parse_args()

    bib = Path(args.input)
    out = Path(args.output)
    df = parse_bib_file(bib)
    save_metadata(df, out)
    print(f"Metadata saved to {out} ({len(df)} records)")
