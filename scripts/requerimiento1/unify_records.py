import os
import re
import csv
from pathlib import Path
from unidecode import unidecode

# ===========================================================
# FUNCIONES DE UTILIDAD
# ===========================================================

def normalize_title(title):
    """Normaliza títulos para comparar correctamente"""
    title = title.lower()
    title = unidecode(title)
    title = re.sub(r'\s+', ' ', title).strip()
    return title

def extract_field(entry, field):
    """Extrae un campo (como title o doi) del texto BibTeX"""
    match = re.search(rf'{field}\s*=\s*{{(.*?)}}', entry, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return ""

def read_bib_files(input_dirs):
    """Lee todos los archivos .bib dentro de las carpetas dadas"""
    entries = []
    for folder in input_dirs:
        folder_path = Path(folder)
        if not folder_path.exists():
            continue
        for file in folder_path.glob("*.bib"):
            with open(file, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                raw_entries = re.findall(r'@\w+\s*{[^@]*}', content, re.DOTALL)
                for entry in raw_entries:
                    entries.append((file.name, entry))
    return entries

# ===========================================================
# PROCESO PRINCIPAL
# ===========================================================

def unify_bib_files():
    base_path = Path("data")
    output_dir = base_path / "processed"
    log_dir = base_path / "logs"
    output_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)

    # Carpetas de entrada (ajústalas si tus datos están en otra ruta)
    input_dirs = [
        "data/raw/IEEE",
        "data/raw/SemanticScholar",
    ]

    print("Leyendo archivos .bib...")
    all_entries = read_bib_files(input_dirs)
    print(f"Total de entradas leídas: {len(all_entries)}")

    seen = {}
    unique_entries = []
    duplicates = []

    for source_file, entry in all_entries:
        doi = extract_field(entry, "doi")
        title = extract_field(entry, "title")
        entry_type = re.search(r'^@(\w+)', entry).group(1) if re.search(r'^@(\w+)', entry) else "unknown"

        key = doi.lower().strip() if doi else normalize_title(title)
        if not key:
            continue  # Ignorar si no tiene identificadores

        if key not in seen:
            seen[key] = {
                "entry": entry,
                "file": source_file,
                "doi": doi,
                "title": title,
                "type": entry_type
            }
            unique_entries.append(entry)
        else:
            duplicates.append({
                "duplicated_in": source_file,
                "original_file": seen[key]["file"],
                "title": title or "(sin título)",
                "doi": doi or "(sin DOI)",
                "type": entry_type
            })

    # ===========================================================
    # Guardar resultados
    # ===========================================================

    unified_path = output_dir / "unified_references.bib"
    duplicates_path = log_dir / "removed_duplicates.csv"

    # Escribir archivo unificado
    with open(unified_path, "w", encoding="utf-8") as f:
        f.write("\n\n".join(unique_entries))
    print(f"\n✓ Archivo unificado guardado en: {unified_path}")

    # Escribir registro de duplicados
    with open(duplicates_path, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["title", "doi", "type", "original_file", "duplicated_in"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for dup in duplicates:
            writer.writerow(dup)
    print(f"✓ Registro de duplicados guardado en: {duplicates_path}")

    print("\nResumen:")
    print(f"  Entradas totales: {len(all_entries)}")
    print(f"  Entradas únicas: {len(unique_entries)}")
    print(f"  Duplicados eliminados: {len(duplicates)}")


if __name__ == "__main__":
    unify_bib_files()
