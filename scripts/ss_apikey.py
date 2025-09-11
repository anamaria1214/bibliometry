import requests
import time
from pathlib import Path
from datetime import datetime

BASE_URL = "https://api.semanticscholar.org/graph/v1/paper/search"

API_KEY = "TU_API_KEY_AQUI"

FIELDS = "title,authors,year,url,abstract"

def search_semantic_scholar(query, limit=100, offset=0):
    headers = {"x-api-key": API_KEY} if API_KEY else {}
    params = {
        "query": query,
        "limit": limit,
        "offset": offset,
        "fields": FIELDS
    }
    response = requests.get(BASE_URL, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

def save_to_bib(data, output_dir="data/raw"):
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

    print(f"\n Done! {len(data)} papers saved in '{filename}'")

def main():
    query = input("Enter your search term: ")
    results = []
    offset = 0
    total = None

    print(f"Searching Semantic Scholar for '{query}'...")

    while True:
        batch = search_semantic_scholar(query, limit=100, offset=offset)
        if batch and "data" in batch:
            papers = batch["data"]
            if total is None:
                total = batch.get("total", len(papers))
                print(f"Total results available: {total}")

            results.extend(papers)
            print(f"Downloaded {len(results)}/{total} papers...")

            if len(results) >= total or len(papers) == 0:
                break
        else:
            break

        offset += 100
        time.sleep(1)

    if results:
        save_to_bib(results)
    else:
        print("\n No papers found.")

if __name__ == "__main__":
    main()
