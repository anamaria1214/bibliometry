from datetime import datetime
from pathlib import Path
import time


def download_semantic_scholar(search_query: str = "generative artificial intelligence", max_results: int = 1000,
                             limit: int = 20, max_retries: int = 5):
    """
    Descarga artículos de Semantic Scholar con manejo de rate limits (429) y backoff.
    - limit: cantidad por página (se recomienda 10-50)
    - max_retries: reintentos por petición en caso de 429 u errores transitorios
    """
    import requests
    import random

    output_dir = Path("data/raw")
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"{'='*60}")
    print(f"Descargando desde Semantic Scholar: {search_query}")
    print(f"{'='*60}\n")

    all_papers = []
    offset = 0

    try:
        while len(all_papers) < max_results:
            to_request = min(limit, max_results - len(all_papers))
            print(f"Solicitando papers (offset: {offset}, limit: {to_request})...")

            url = "https://api.semanticscholar.org/graph/v1/paper/search"
            params = {
                'query': search_query,
                'offset': offset,
                'limit': to_request,
                'fields': 'title,authors,year,venue,citationCount,abstract,externalIds'
            }

            retries = 0
            while True:
                try:
                    response = requests.get(url, params=params, timeout=30)
                except requests.RequestException as e:
                    retries += 1
                    if retries > max_retries:
                        print(f"✗ Error de petición repetido: {e} (abortando)")
                        raise
                    sleep_time = 2 ** retries + random.random()
                    print(f"✗ Request failed: {e}. Reintentando en {sleep_time:.1f}s ({retries}/{max_retries})")
                    time.sleep(sleep_time)
                    continue

                # Manejo de rate limit
                if response.status_code == 429:
                    retries += 1
                    retry_after = response.headers.get('Retry-After')
                    if retry_after:
                        try:
                            wait = int(retry_after)
                        except ValueError:
                            wait = 2 ** retries
                    else:
                        wait = 2 ** retries
                    # añadir jitter
                    wait = wait + random.uniform(0, 1)
                    if retries > max_retries:
                        print(f"✗ Recibido 429 demasiadas veces. Abortando petición.")
                        raise RuntimeError("Rate limited by Semantic Scholar API")
                    print(f"✗ 429 Rate limit. Esperando {wait:.1f}s antes de reintentar ({retries}/{max_retries})")
                    time.sleep(wait)
                    continue

                if response.status_code != 200:
                    print(f"✗ Error en API: {response.status_code}")
                    # No intentar indefinidamente; romper el bucle principal
                    raise RuntimeError(f"API error {response.status_code}")

                # éxito
                data = response.json()
                papers = data.get('data', [])

                if not papers:
                    print("✗ No hay más resultados")
                    break

                all_papers.extend(papers)
                print(f"  ✓ Obtenidos {len(papers)} papers (Total: {len(all_papers)})")

                offset += len(papers)
                # pequeño sleep entre páginas para ser conservador
                time.sleep(1 + random.uniform(0, 0.5))
                break

            # fin while retries
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
                # Generar citation key
                first_author = paper.get('authors', [{}])[0].get('name', 'Unknown').split()[-1]
                year = paper.get('year', 'n.d.')
                citation_key = f"{first_author}{year}_{i}"

                # Crear entrada BibTeX
                title = paper.get('title', 'Untitled').replace('{', '').replace('}', '')
                authors = ' and '.join([a.get('name', '') for a in paper.get('authors', [])])
                venue = paper.get('venue', 'Unknown')
                abstract = paper.get('abstract', '')

                # Determinar tipo (article o inproceedings)
                entry_type = 'inproceedings' if 'conference' in venue.lower() or 'proceedings' in venue.lower() else 'article'

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

                # Agregar DOI si existe
                external_ids = paper.get('externalIds', {})
                if 'DOI' in external_ids:
                    bibtex_entry += f"  doi = {{{external_ids['DOI']}}},\n"

                bibtex_entry += "}\n\n"
                bibtex_content += bibtex_entry

            except Exception as e:
                print(f"  ✗ Error procesando paper {i}: {e}")
                continue

        entries_count = bibtex_content.count('@')
        if entries_count == 0:
            print("No se obtuvieron entradas válidas; no se crea archivo .bib")
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = output_dir / f"semantic_scholar_{timestamp}.bib"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(bibtex_content)
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
