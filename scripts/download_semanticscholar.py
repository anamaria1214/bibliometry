import requests
import time
from pathlib import Path
from datetime import datetime

# URL base de Semantic Scholar API
BASE_URL = "https://api.semanticscholar.org/graph/v1/paper/search"

# Solo pedimos campos permitidos
FIELDS = "title,authors,year,url,abstract"

def search_semantic_scholar(query, limit=100, offset=0):
    """
    Realiza una búsqueda en Semantic Scholar.
    """
    params = {
        "query": query,
        "limit": limit,
        "offset": offset,
        "fields": FIELDS
    }
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

def save_to_bib(data, output_dir="data/raw"):
    """
    Guarda los resultados en un archivo .bib dentro de /data/raw
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = Path(output_dir) / f"semantic_scholar_{timestamp}.bib"

    with open(filename, "w", encoding="utf-8") as f:
        for idx, paper in enumerate(data, 1):
            title = paper.get("title", "").replace("{", "").replace("}", "")
            authors = " and ".join([a["name"] for a in paper.get("authors", [])])
            year = paper.get("year", "")
            url = paper.get("url", "")
            abstract = paper.get("abstract", "")

            # Generar clave (ej: FirstAuthorYear)
            key = f"{authors.split()[0]}{year}" if authors else f"paper{idx}"

            f.write(f"@article{{{key},\n")
            f.write(f"  title = {{{title}}},\n")
            if authors:
                f.write(f"  author = {{{authors}}},\n")
            if year:
                f.write(f"  year = {{{year}}},\n")
            if url:
                f.write(f"  url = {{{url}}},\n")
            if abstract:
                f.write(f"  abstract = {{{abstract}}},\n")
            f.write("}\n\n")

    print(f"Done! {len(data)} papers saved in '{filename}'")

def main():
    query = input("Enter your search term: ")
    max_results = int(input("Enter number of results (e.g. 200): "))
    results = []

    print(f"Searching Semantic Scholar for '{query}'...")

    # Paginación
    offset = 0
    while offset < max_results:
        batch = search_semantic_scholar(query, limit=100, offset=offset)
        if batch and "data" in batch:
            papers = batch["data"]
            results.extend(papers)
            print(f"Downloaded {len(results)} papers...")

            if len(papers) == 0:
                break
        else:
            break

        offset += 100
        time.sleep(1)  # evitar saturar API

    # Guardar en .bib
    if results:
        save_to_bib(results)
    else:
        print("No papers found.")

if __name__ == "__main__":
    main()
