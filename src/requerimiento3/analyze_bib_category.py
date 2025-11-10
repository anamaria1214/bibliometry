"""
analyze_bib_category.py

Lee data/processed/unified_references.bib, extrae abstracts y:
 - calcula frecuencia de las 15 palabras semilla (por ocurrencias y por #abstracts)
 - descubre hasta 15 términos asociados con TF-IDF (excluyendo semillas)
 - calcula "precisión" de cada término descubierto: máxima similitud coseno con alguna semilla
 - guarda outputs en data/analysis/

Requisitos:
 pip install scikit-learn pandas unidecode bibtexparser
"""

import re
from pathlib import Path
from collections import Counter, defaultdict
import csv
import json
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from unidecode import unidecode

# --------------------------
# Configuración / Semillas
# --------------------------

# Calcular la ruta raíz del proyecto (2 niveles arriba desde este archivo)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
BIB_PATH = PROJECT_ROOT / "data/processed/unified_references.bib"
OUTPUT_DIR = PROJECT_ROOT / "data/analysis"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CATEGORY_NAME = "Concepts of Generative AI in Education"

SEED_TERMS = [
    "Generative models",
    "Prompting",
    "Machine learning",
    "Multimodality",
    "Fine-tuning",
    "Training data",
    "Algorithmic bias",
    "Explainability",
    "Transparency",
    "Ethics",
    "Privacy",
    "Personalization",
    "Human-AI interaction",
    "AI literacy",
    "Co-creation"
]

# Normalización helper
def normalize_text(s: str) -> str:
    s = s or ""
    s = unidecode(s)              # quitar tildes
    s = s.lower()
    # mantener alfanum y espacios
    s = re.sub(r"[^a-z0-9\s\-]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

# Normalizar semillas para búsqueda / comparación
SEED_TERMS_NORM = [normalize_text(t) for t in SEED_TERMS]

# --------------------------
# 1) Extraer abstracts
# --------------------------

def read_bib_file_extract_abstracts(bib_path: Path):
    """
    Lee el .bib y extrae la lista de abstracts.
    Retorna lista de dicts: [{'id': key_or_index, 'title':..., 'abstract':...}, ...]
    """
    text = bib_path.read_text(encoding="utf-8", errors="ignore")
    # separar por entradas: busca patrones @TYPE{...}
    raw_entries = re.findall(r'@[\w]+\s*{[^@]*}', text, flags=re.DOTALL | re.IGNORECASE)
    results = []
    for idx, entry in enumerate(raw_entries, start=1):
        # intentar extraer key (después de @TYPE{KEY,)
        mkey = re.match(r'@[\w]+\s*{\s*([^,]+),', entry)
        key = mkey.group(1).strip() if mkey else f"entry_{idx}"
        # extraer title (opcional)
        title = ""
        mtitle = re.search(r'title\s*=\s*[{"](.+?)[}"]\s*,', entry, flags=re.IGNORECASE | re.DOTALL)
        if mtitle:
            title = mtitle.group(1).strip().replace("\n", " ")
        # extraer abstract (robusto a saltos de linea)
        mabs = re.search(r'abstract\s*=\s*[{"](.+?)[}"]\s*,', entry, flags=re.IGNORECASE | re.DOTALL)
        abstract = ""
        if mabs:
            abstract = mabs.group(1).strip().replace("\n", " ")
        # fallback: buscar 'abstract=' sin coma final
        if not abstract:
            mabs2 = re.search(r'abstract\s*=\s*[{"](.+?)[}"]\s*$', entry, flags=re.IGNORECASE | re.DOTALL)
            if mabs2:
                abstract = mabs2.group(1).strip().replace("\n", " ")
        results.append({
            "key": key,
            "title": title,
            "abstract": abstract
        })
    return results

# --------------------------
# 2) Conteos para semillas
# --------------------------

def count_seed_terms_in_abstracts(abstracts, seed_terms_norm):
    """
    devuelve:
      - total_occurrences: Counter(term -> total token occurrences across all abstracts)
      - abstracts_count: Counter(term -> number of abstracts where term appears at least once)
    Buscamos matches de frase (multiword) y también variantes stemming mínimas (present/ing/plural).
    Para simplicidad coincidimos por substring sobre versión normalizada.
    """
    total_occ = Counter()
    abstracts_occ = Counter()
    for item in abstracts:
        abs_text = normalize_text(item["abstract"])
        for term_raw, term_norm in zip(SEED_TERMS, seed_terms_norm):
            if not term_norm:
                continue
            # contar como substring (palabras adyacentes) para multi-word
            # usamos boundaries: buscar term_norm como secuencia de tokens
            # Para contar occurrences: contar las veces que aparece la secuencia
            occurrences = len(re.findall(r'\b' + re.escape(term_norm) + r'\b', abs_text))
            # como fallback probar presencia por palabras sueltas (por ejemplo "prompting" vs "prompt")
            if occurrences == 0:
                # contar presencia aproximada por tokens
                # dividir tokens y ver si cualquier token del term_norm aparece
                term_tokens = term_norm.split()
                token_occ = sum(1 for tok in term_tokens if re.search(r'\b' + re.escape(tok) + r'\b', abs_text))
                if token_occ > 0:
                    occurrences = token_occ  # conteo aproximado
            if occurrences > 0:
                total_occ[term_raw] += occurrences
                abstracts_occ[term_raw] += 1
    return total_occ, abstracts_occ

# --------------------------
# 3) TF-IDF discovery
# --------------------------

def discover_terms_with_tfidf(abstract_texts, seed_terms_norm, top_n=15, ngram_range=(1,2), max_features=5000):
    """
    Construye TF-IDF sobre abstracts (preprocesados) y selecciona los top_n términos
    por suma de TF-IDF en el corpus, excluyendo las semillas.
    Retorna list of dicts: [{'term':..., 'tfidf_sum':..., 'doc_freq':..., 'tfidf_vector': col_vec}, ...]
    """
    # Preprocess documents
    docs = [normalize_text(t) for t in abstract_texts]

    vectorizer = TfidfVectorizer(ngram_range=ngram_range, max_features=max_features,
                                 stop_words='english', token_pattern=r'(?u)\b\w+\b', min_df=2)
    X = vectorizer.fit_transform(docs)  # shape (n_docs, n_terms)
    feature_names = np.array(vectorizer.get_feature_names_out())

    # sum TF-IDF per term across docs
    tfidf_sum = np.asarray(X.sum(axis=0)).ravel()
    # document frequency (#docs where term appears)
    doc_freq = np.asarray((X > 0).sum(axis=0)).ravel()

    # build candidate list excluding seed terms (normalized)
    seed_set = set(seed_terms_norm)
    candidates = []
    for i, fname in enumerate(feature_names):
        if fname in seed_set:
            continue
        # also exclude single-char tokens or pure numbers
        if len(fname) < 2 or fname.isdigit():
            continue
        candidates.append((fname, tfidf_sum[i], doc_freq[i], i))

    # sort by tfidf_sum desc
    candidates_sorted = sorted(candidates, key=lambda x: x[1], reverse=True)
    selected = []
    for fname, s, df, idx_col in candidates_sorted[:top_n*5]:  # take a pool then filter
        # filter out tokens that are substrings of seed terms or viceversa (to reduce redundancy)
        normalized = fname
        # skip if equals any seed token by containment
        skip = False
        for st in seed_set:
            if normalized == st or normalized in st or st in normalized:
                skip = True
                break
        if skip:
            continue
        selected.append({
            "term": fname,
            "tfidf_sum": float(s),
            "doc_freq": int(df),
            "col_index": int(idx_col)
        })
        if len(selected) >= top_n:
            break

    # Return vectorizer and X too for similarity computations
    return selected, vectorizer, X

# --------------------------
# 4) Similarity / Precision
# --------------------------

def compute_similarity_to_seeds(selected_terms, vectorizer, X, seed_terms_norm, abstract_texts):
    """
    Para cada selected term, toma su columna vector (across docs) y calcula similitud coseno
    con cada seed term columna (si seed exists in vectorizer vocab). Si seed no está en vocab,
    construye su column vector sum of token columns (approx).
    Devuelve lista con similitud máxima por término.
    """
    feature_names = np.array(vectorizer.get_feature_names_out())
    term_to_index = {t: i for i, t in enumerate(feature_names)}

    # build column vectors for seeds when possible
    n_docs = X.shape[0]
    seed_vectors = {}
    for seed_raw, seed_norm in zip(SEED_TERMS, seed_terms_norm):
        if seed_norm in term_to_index:
            col_idx = term_to_index[seed_norm]
            vec = X[:, col_idx].toarray().ravel()
            seed_vectors[seed_raw] = vec
        else:
            # attempt to build by summing constituent tokens if seed is multiword
            tokens = seed_norm.split()
            cols = []
            for tk in tokens:
                if tk in term_to_index:
                    cols.append(X[:, term_to_index[tk]].toarray().ravel())
            if cols:
                seed_vectors[seed_raw] = np.sum(np.vstack(cols), axis=0)
            else:
                # fallback: zero vector
                seed_vectors[seed_raw] = np.zeros(n_docs)

    # compute for each selected term
    results = []
    for sel in selected_terms:
        term = sel["term"]
        col_idx = sel["col_index"]
        term_vec = X[:, col_idx].toarray().ravel()
        # if term_vec is zero (shouldn't), skip
        if np.linalg.norm(term_vec) == 0:
            max_sim = 0.0
            best_seed = None
        else:
            sims = {}
            for seed_raw, seed_vec in seed_vectors.items():
                # if seed_vec is zero skip
                if np.linalg.norm(seed_vec) == 0:
                    sims[seed_raw] = 0.0
                else:
                    s = cosine_similarity(term_vec.reshape(1, -1), seed_vec.reshape(1, -1))[0,0]
                    sims[seed_raw] = float(s)
            # find best
            best_seed = max(sims, key=sims.get)
            max_sim = sims[best_seed]
        sel_out = dict(sel)
        sel_out.update({
            "best_seed_match": best_seed,
            "max_similarity_to_seed": float(max_sim)
        })
        results.append(sel_out)
    return results

# --------------------------
# 5) Save outputs
# --------------------------

def save_seed_frequency_csv(total_occ, abstracts_occ, out_path):
    rows = []
    for term in SEED_TERMS:
        rows.append({
            "category": CATEGORY_NAME,
            "seed_term": term,
            "total_occurrences": int(total_occ.get(term, 0)),
            "num_abstracts_with_term": int(abstracts_occ.get(term, 0))
        })
    df = pd.DataFrame(rows)
    df.to_csv(out_path, index=False, encoding="utf-8")
    return df

def save_auto_terms_csv(auto_terms, out_path):
    # auto_terms: list of dicts with fields term, tfidf_sum, doc_freq, best_seed_match, max_similarity_to_seed
    rows = []
    for t in auto_terms:
        rows.append({
            "term": t["term"],
            "tfidf_sum": t["tfidf_sum"],
            "doc_freq": t["doc_freq"],
            "best_seed_match": t.get("best_seed_match", ""),
            "max_similarity_to_seed": t.get("max_similarity_to_seed", 0.0)
        })
    df = pd.DataFrame(rows)
    df.to_csv(out_path, index=False, encoding="utf-8")
    return df

def save_precision_report(auto_terms, seed_df, out_path, similarity_threshold=0.30):
    """
    Precision: proporción de auto_terms whose max_similarity_to_seed >= threshold
    Also compute exact overlap count (term equals any seed term)
    """
    total = len(auto_terms)
    if total == 0:
        precision = 0.0
    else:
        hits = sum(1 for t in auto_terms if t.get("max_similarity_to_seed", 0.0) >= similarity_threshold)
        precision = hits / total

    # exact overlap
    seed_set_norm = set(SEED_TERMS_NORM)
    exact_overlaps = []
    for t in auto_terms:
        if normalize_text(t["term"]) in seed_set_norm:
            exact_overlaps.append(t["term"])

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(f"Category: {CATEGORY_NAME}\n")
        f.write(f"Seed terms (count): {len(SEED_TERMS)}\n")
        f.write("\n--- Seed frequency summary ---\n")
        f.write(seed_df.to_string(index=False))
        f.write("\n\n--- Auto-discovered terms ---\n")
        for t in auto_terms:
            f.write(json.dumps(t, ensure_ascii=False) + "\n")
        f.write("\n--- Precision summary ---\n")
        f.write(f"Similarity threshold (recommended): {similarity_threshold}\n")
        f.write(f"Auto-discovered terms total: {total}\n")
        f.write(f"Auto-discovered terms with similarity >= threshold: {hits}\n")
        f.write(f"Precision (hits / total): {precision:.3f}\n")
        f.write(f"Exact overlap count (term equals seed): {len(exact_overlaps)}\n")
        if exact_overlaps:
            f.write("Exact overlaps: " + ", ".join(exact_overlaps) + "\n")
        f.write("\nInterpretation:\n")
        f.write("- Un término se considera 'preciso' si su vector TF-IDF a lo largo del corpus\n")
        f.write(f"  tiene similitud coseno >= {similarity_threshold} con algún término semilla.\n")
        f.write("- Umbral sugerido 0.30 (valor heurístico). Ajusta si deseas mayor/menor estricticidad.\n")

# --------------------------
# MAIN
# --------------------------

def main():
    print("Leyendo .bib y extrayendo abstracts...")
    entries = read_bib_file_extract_abstracts(BIB_PATH)
    # filtrar solo abstracts no vacíos
    abstracts = [e for e in entries if e["abstract"].strip()]
    print(f"Total entradas en .bib: {len(entries)}; con abstract: {len(abstracts)}")

    abstract_texts = [e["abstract"] for e in abstracts]

    # 2) Conteos semillas
    print("Contando términos semilla en abstracts...")
    total_occ, abstracts_occ = count_seed_terms_in_abstracts(abstracts, SEED_TERMS_NORM)
    seed_csv = OUTPUT_DIR / "category_frequencies.csv"
    seed_df = save_seed_frequency_csv(total_occ, abstracts_occ, seed_csv)
    print(f"Seed frequencies saved to {seed_csv}")

    # 3) Descubrir términos con TF-IDF
    print("Calculando TF-IDF y descubriendo términos asociados...")
    selected, vectorizer, X = discover_terms_with_tfidf(abstract_texts, SEED_TERMS_NORM, top_n=15,
                                                       ngram_range=(1,2), max_features=8000)
    print(f"Selected {len(selected)} candidate terms")

    # 4) Similaridades con semillas
    print("Calculando similitudes de términos descubiertos con semillas...")
    auto_terms_with_sim = compute_similarity_to_seeds(selected, vectorizer, X, SEED_TERMS_NORM, abstract_texts)

    # 5) Guardar outputs
    auto_csv = OUTPUT_DIR / "auto_discovered_terms.csv"
    auto_df = save_auto_terms_csv(auto_terms_with_sim, auto_csv)
    print(f"Auto-discovered terms saved to {auto_csv}")

    report_txt = OUTPUT_DIR / "precision_report.txt"
    save_precision_report(auto_terms_with_sim, seed_df, report_txt, similarity_threshold=0.30)
    print(f"Precision report saved to {report_txt}")

    print("\n--- Resumen ---")
    print(f"Seed terms file: {seed_csv}")
    print(f"Auto-discovered terms file: {auto_csv}")
    print(f"Precision report: {report_txt}")

if __name__ == "__main__":
    main()
