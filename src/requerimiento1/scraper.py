from playwright.sync_api import sync_playwright
from datetime import datetime
from pathlib import Path
import time
import re
import random

# Calcular la ruta raíz del proyecto
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

def download_semantic_scholar(search_query: str = "generative artificial intelligence", max_results: int = 1000):
    """
    Descarga artículos de Semantic Scholar (API pública disponible)
    """
    import requests
    
    output_dir = PROJECT_ROOT / "data/raw"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"{'='*60}")
    print(f"Descargando desde Semantic Scholar: {search_query}")
    print(f"{'='*60}\n")
    
    all_papers = []
    offset = 0
    limit = 100
    
    try:
        def fetch_with_retries(url, params, max_retries=5):
            attempt = 0
            while attempt <= max_retries:
                resp = requests.get(url, params=params)
                if resp.status_code == 200:
                    return resp
                # Retry on 429 (rate limit) or 5xx server errors
                if resp.status_code == 429 or 500 <= resp.status_code < 600:
                    backoff = (2 ** attempt) + random.uniform(0, 1)
                    print(f"✗ API returned {resp.status_code}. Retry in {backoff:.1f}s (attempt {attempt+1}/{max_retries})")
                    time.sleep(backoff)
                    attempt += 1
                    continue
                # Other errors -> return None
                print(f"✗ Error en API: {resp.status_code}")
                return None
            return None

        while len(all_papers) < max_results:
            print(f"Solicitando papers (offset: {offset})...")

            url = "https://api.semanticscholar.org/graph/v1/paper/search"
            params = {
                'query': search_query,
                'offset': offset,
                'limit': limit,
                'fields': 'title,authors,year,venue,citationCount,abstract,externalIds'
            }

            response = fetch_with_retries(url, params)
            if response is None:
                print("✗ No se pudo obtener respuesta de la API tras reintentos. Abortando descarga.")
                break

            data = response.json()
            papers = data.get('data', []) if isinstance(data, dict) else []

            if not papers:
                print("✗ No hay más resultados")
                break

            all_papers.extend(papers)
            print(f"  ✓ Obtenidos {len(papers)} papers (Total: {len(all_papers)})")

            offset += limit
            # Back off a bit (could be tuned)
            time.sleep(1 + random.uniform(0, 1))  # Respetar rate limit

            if len(all_papers) >= max_results:
                all_papers = all_papers[:max_results]
                break
        
        # Convertir a BibTeX
        print(f"\n{'='*60}")
        print("Generando archivo BibTeX...")
        print(f"{'='*60}\n")
        
        bibtex_content = ""
        
        for i, paper in enumerate(all_papers):
            try:
                # Generar citation key (proteger contra nombres vacíos)
                authors_list = paper.get('authors') or []
                if authors_list and isinstance(authors_list, list):
                    first_name = authors_list[0].get('name') or ''
                    name_tokens = first_name.split()
                    first_author = name_tokens[-1] if name_tokens else 'Unknown'
                else:
                    first_author = 'Unknown'

                year = paper.get('year') or 'n.d.'
                citation_key = f"{first_author}{year}_{i}"

                # Crear entrada BibTeX
                title = (paper.get('title') or 'Untitled').replace('{', '').replace('}', '')
                authors = ' and '.join([a.get('name', '') for a in authors_list])
                venue = paper.get('venue') or 'Unknown'
                abstract = paper.get('abstract') or ''

                # Determinar tipo (article o inproceedings)
                try:
                    venue_lower = venue.lower()
                except Exception:
                    venue_lower = ''
                entry_type = 'inproceedings' if 'conference' in venue_lower or 'proceedings' in venue_lower else 'article'

                bibtex_entry = f"@{entry_type}{{{citation_key},\n"
                bibtex_entry += f"  title = {{{title}}},\n"
                bibtex_entry += f"  author = {{{authors}}},\n"
                bibtex_entry += f"  year = {{{year}}},\n"

                if entry_type == 'article':
                    bibtex_entry += f"  journal = {{{venue}}},\n"
                else:
                    bibtex_entry += f"  booktitle = {{{venue}}},\n"

                if abstract:
                    bibtex_entry += f"  abstract = {{{abstract}}},\n"

                # Agregar DOI si existe (case-insensitive)
                external_ids = paper.get('externalIds') or {}
                doi = None
                for k, v in external_ids.items():
                    if k.lower() == 'doi' and v:
                        doi = v
                        break
                if doi:
                    bibtex_entry += f"  doi = {{{doi}}},\n"

                bibtex_entry += "}\n\n"
                bibtex_content += bibtex_entry

            except Exception as e:
                print(f"  ✗ Error procesando paper {i}: {e}")
                continue
        
        # Guardar archivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"semantic_scholar_{timestamp}.bib"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(bibtex_content)
        
        entries_count = bibtex_content.count('@')
        print(f"Archivo guardado: {output_file}")
        print(f"Total de entradas: {entries_count}")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")



if __name__ == "__main__":
    print("="*60)
    print("SCRAPER SEMANTIC SCHOLAR")
    print("="*60)
    print("Semantic Scholar (Multidisciplinario - API PÚBLICA)")
    
    search_query = input("Término de búsqueda [generative artificial intelligence]: ").strip()
    if not search_query:
        search_query = "generative artificial intelligence"
    
    max_results = input("Número máximo de resultados [1000]: ").strip()
    max_results = int(max_results) if max_results else 1000
    
    print()

    download_semantic_scholar(search_query, max_results)
    
    print("\n" + "="*60)
    print("✓ PROCESO COMPLETADO")
    print("="*60) 