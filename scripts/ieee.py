import requests
import json
import os

SEARCH_TERM = "machine learning"
URL = f"https://ieeexplore.ieee.org/rest/search"

params = {
    "newsearch": True,
    "queryText": SEARCH_TERM,
    "highlight": True,
    "returnFacets": ["ALL"],
    "returnType": "SEARCH"
}

resp = requests.post(URL, json=params)
data = resp.json()

# Guardar resultados
os.makedirs("data/raw", exist_ok=True)
with open("data/raw/ieee_api.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print("Archivo guardado en data/raw/ieee_api.json")
