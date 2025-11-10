# Similitud textual - Streamlit app
# Requerimiento 2: Implementar 4 algoritmos clásicos y 2 basados en modelos IA.
# Uso: streamlit run src/requerimiento2/similitud_textual_app.py
# Requisitos pip (instala en tu venv):
# pip install streamlit bibtexparser scikit-learn pandas numpy sentence-transformers rapidfuzz

import streamlit as st
import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import author
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from rapidfuzz.distance import Levenshtein
from io import StringIO

# Calcular la ruta raíz del proyecto
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

st.set_page_config(page_title='Análisis similitud textual', layout='wide')

st.title('Análisis de similitud textual — Requerimiento 2')
st.markdown('Este app permite seleccionar artículos desde un archivo .bib, extraer los abstracts y comparar similitud con 4 algoritmos clásicos y 2 modelos de IA (sentence-transformers).')

# Sidebar: path al archivo .bib
default_bib_path = str(PROJECT_ROOT / 'data/processed/unified_references.bib')
path = st.sidebar.text_input('Ruta del archivo .bib (path)', value=default_bib_path)

@st.cache_data
def load_bib(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read()
    except Exception as e:
        return None, f'Error abriendo archivo: {e}'
    parser = BibTexParser(common_strings=True)
    parser.customization = author
    try:
        bib_database = bibtexparser.loads(text, parser=parser)
    except Exception as e:
        return None, f'Error parseando .bib: {e}'
    entries = bib_database.entries
    # Extract title and abstract
    items = []
    for i, e in enumerate(entries):
        title = e.get('title', f'No title {i}')
        abstract = e.get('abstract', e.get('note', ''))
        key = e.get('ID', str(i))
        items.append({'key': key, 'title': title, 'abstract': abstract, 'raw': e})
    return items, None

items, err = load_bib(path)
if err:
    st.error(err)
    st.stop()
if not items:
    st.warning('No se encontraron entradas en el .bib')
    st.stop()

# Show list of articles
titles = [f"[{it['key']}] {it['title']}" for it in items]
sel = st.multiselect('Selecciona dos o más artículos para comparar (ctrl/cmd+click)', options=titles)

if len(sel) < 2:
    st.info('Selecciona al menos dos artículos para ejecutar el análisis.')
    st.stop()

# Map selection to abstracts
selected_indices = [titles.index(s) for s in sel]
selected = [items[i] for i in selected_indices]
abstracts = [it['abstract'] if it['abstract'] else '' for it in selected]
ids = [it['key'] for it in selected]

st.subheader('Abstracts seleccionados')
for i, it in enumerate(selected):
    st.markdown(f"**{ids[i]} — {it['title']}**")
    st.write(abstracts[i])

# ---------- ALGORITMOS CLÁSICOS ----------
st.header('Algoritmos clásicos')

# 1) Distancia de edición (Levenshtein) con matriz DP explicada
@st.cache_data
def levenshtein_matrix(a, b):
    # returns matrix (len(a)+1 x len(b)+1)
    n = len(a); m = len(b)
    D = np.zeros((n+1, m+1), dtype=int)
    for i in range(n+1):
        D[i,0] = i
    for j in range(m+1):
        D[0,j] = j
    for i in range(1, n+1):
        for j in range(1, m+1):
            cost = 0 if a[i-1]==b[j-1] else 1
            D[i,j] = min(D[i-1,j] + 1,      # deletion
                         D[i,j-1] + 1,      # insertion
                         D[i-1,j-1] + cost) # substitution
    return D

# 2) Jaccard similarity on character n-grams
def char_ngrams(s, n=3):
    s = s.replace('\n',' ').strip().lower()
    return set([s[i:i+n] for i in range(max(0, len(s)-n+1))])

def jaccard_set(a,b):
    if not a and not b:
        return 1.0
    inter = len(a & b)
    union = len(a | b)
    return inter/union if union>0 else 0.0

# 3) Sørensen–Dice (bigramas)
def dice_coefficient(a,b):
    if not a and not b:
        return 1.0
    inter = len(a & b)
    return 2*inter / (len(a) + len(b)) if (len(a)+len(b))>0 else 0.0

# 4) TF-IDF + Cosine similarity
@st.cache_data
def tfidf_cosine(docs):
    vect = TfidfVectorizer(stop_words='english')
    X = vect.fit_transform(docs)
    sim = cosine_similarity(X)
    return sim, vect

# ---------- MODELOS IA (sentence-transformers) ----------
st.header('Modelos IA (embeddings)')
model_choice = st.selectbox('Seleccionar modelo de sentence-transformers para embeddings', options=['all-MiniLM-L6-v2','all-mpnet-base-v2'])
@st.cache_data
def load_sbert(name):
    return SentenceTransformer(name)

model = load_sbert(model_choice)

# Compute pairwise comparisons
n = len(abstracts)

# Prepare pairwise matrices
lev_matrix = np.zeros((n,n), dtype=int)
lev_dp_examples = {}  # store DP matrix for each pair (i,j)
jaccard_mat = np.zeros((n,n))
dice_mat = np.zeros((n,n))
tfidf_sim, tfidf_vect = tfidf_cosine(abstracts)

# embeddings using two IA models: chosen model + a second different one
@st.cache_data
def embed_texts(_model, texts):
    return model.encode(texts, show_progress_bar=True)

emb1 = embed_texts(model, abstracts)
# For the second IA model, we will use the other pre-trained S-BERT
second_model_name = 'all-mpnet-base-v2' if model_choice!='all-mpnet-base-v2' else 'all-MiniLM-L6-v2'
second_model = load_sbert(second_model_name)
emb2 = embed_texts(second_model, abstracts)

for i in range(n):
    for j in range(n):
        # Levenshtein distance (on raw text)
        a = abstracts[i]
        b = abstracts[j]
        # rapidfuzz Levenshtein gives distance directly but we provide DP matrix as explanation
        D = levenshtein_matrix(a,b)
        lev_matrix[i,j] = int(D[-1,-1])
        lev_dp_examples[(i,j)] = D
        # Jaccard on char trigrams
        A = char_ngrams(a, n=3)
        B = char_ngrams(b, n=3)
        jaccard_mat[i,j] = jaccard_set(A,B)
        # Dice on bigrams
        A2 = char_ngrams(a, n=2)
        B2 = char_ngrams(b, n=2)
        dice_mat[i,j] = dice_coefficient(A2,B2)

# Cosine matrices for embeddings
cos_emb1 = cosine_similarity(emb1)
cos_emb2 = cosine_similarity(emb2)

# ---------- Mostrar resultados ----------
st.header('Resultados - matrices de similitud / distancia')
col1, col2 = st.columns(2)
with col1:
    st.subheader('Distancia Levenshtein (matriz)')
    df_lev = pd.DataFrame(lev_matrix, index=ids, columns=ids)
    st.dataframe(df_lev)
with col2:
    st.subheader('Jaccard (char 3-grams)')
    st.dataframe(pd.DataFrame(jaccard_mat, index=ids, columns=ids).round(4))

col3, col4 = st.columns(2)
with col3:
    st.subheader('Sørensen–Dice (char 2-grams)')
    st.dataframe(pd.DataFrame(dice_mat, index=ids, columns=ids).round(4))
with col4:
    st.subheader('TF-IDF + Cosine')
    st.dataframe(pd.DataFrame(tfidf_sim, index=ids, columns=ids).round(4))

st.subheader('Embeddings (Model 1: ' + model_choice + ') — Cosine similarity')
st.dataframe(pd.DataFrame(cos_emb1, index=ids, columns=ids).round(4))
st.subheader('Embeddings (Model 2: ' + second_model_name + ') — Cosine similarity')
st.dataframe(pd.DataFrame(cos_emb2, index=ids, columns=ids).round(4))

# Detailed step-by-step explanation for a selected pair
st.header('Explicación paso a paso (selecciona un par)')
pair = st.selectbox('Selecciona par (i,j) para ver explicación detallada', options=[f"{i}-{j}" for i in range(n) for j in range(n)])
i_idx, j_idx = map(int, pair.split('-'))

st.subheader(f'Levenshtein entre {ids[i_idx]} y {ids[j_idx]}')
D = lev_dp_examples[(i_idx,j_idx)]
st.markdown('La distancia de Levenshtein se calcula con programación dinámica. Matriz D donde D[i,j] = coste mínimo para transformar prefijo de longitud i de la cadena A en prefijo de longitud j de la cadena B.')
# Show small previews if too large
max_show = 40
A = abstracts[i_idx]
B = abstracts[j_idx]
st.markdown('**A (preview)**: ' + (A[:max_show] + '...' if len(A)>max_show else A))
st.markdown('**B (preview)**: ' + (B[:max_show] + '...' if len(B)>max_show else B))
# Show DP matrix as dataframe with row/col labels
rows = [''] + list(A)
cols = [''] + list(B)
try:
    dfD = pd.DataFrame(D, index=rows, columns=cols)
    st.dataframe(dfD)
except Exception:
    st.write('Matriz demasiado grande para previsualizar directamente. Mostrando valor final:')
    st.write(int(D[-1,-1]))

st.markdown('''
**Explicación matemática (resumen):**

- Inicialización: D[0, j] = j, D[i, 0] = i.
- Recurrencia: D[i,j] = min( D[i-1,j] + 1, D[i,j-1] + 1, D[i-1,j-1] + cost ) donde cost = 0 si A[i-1]==B[j-1] sino 1.
- La distancia final es D[len(A), len(B)].
''')

st.subheader('Jaccard y Dice — pasos')
A3 = char_ngrams(A,3)
B3 = char_ngrams(B,3)
st.markdown(f'Número de trigrams A: {len(A3)}, trigrams B: {len(B3)}')
st.markdown('Ejemplo de algunos trigrams (A): ' + ', '.join(list(A3)[:8]))
st.markdown('Ejemplo de algunos trigrams (B): ' + ', '.join(list(B3)[:8]))
inter = len(A3 & B3)
union = len(A3 | B3)
st.markdown(f'Intersección = {inter}, Unión = {union}, Jaccard = inter/union = {inter}/{union} = {jaccard_mat[i_idx,j_idx]:.4f}')

A2 = char_ngrams(A,2)
B2 = char_ngrams(B,2)
inter2 = len(A2 & B2)
st.markdown(f'Bigrams intersección = {inter2}, Dice = 2*inter/(|A|+|B|) = {dice_mat[i_idx,j_idx]:.4f}')

st.subheader('TF-IDF + Cosine — pasos')
st.markdown('Vectorizamos los abstracts con TF-IDF (tokenización y normalización). Cosine sim = (v1·v2)/(|v1||v2|).')
try:
    st.write('Cosine TF-IDF entre estos dos:', float(tfidf_sim[i_idx,j_idx]))
except Exception:
    st.write('No disponible')

st.subheader('Embeddings (modelos IA) — pasos')
st.markdown('Se usan modelos preentrenados de sentence-transformers para obtener embeddings de cada abstracto. La similitud semántica se calcula como la similitud coseno entre embeddings.')
st.write('Cosine (Model 1):', float(cos_emb1[i_idx,j_idx]))
st.write('Cosine (Model 2):', float(cos_emb2[i_idx,j_idx]))

# Export results CSV
st.header('Exportar resultados')

results = {
    'pair': [f"{ids[i]}__{ids[j]}" for i in range(n) for j in range(n)],
    'levenshtein': [int(lev_matrix[i, j]) for i in range(n) for j in range(n)],
    'jaccard': [float(jaccard_mat[i, j]) for i in range(n) for j in range(n)],
    'dice': [float(dice_mat[i, j]) for i in range(n) for j in range(n)],
    'tfidf_cosine': [float(tfidf_sim[i, j]) for i in range(n) for j in range(n)],
    'emb1_cosine': [float(cos_emb1[i, j]) for i in range(n) for j in range(n)],
    'emb2_cosine': [float(cos_emb2[i, j]) for i in range(n) for j in range(n)],
}

df_results = pd.DataFrame(results)

# Convertir directamente el DataFrame a CSV (texto plano)
csv_data = df_results.to_csv(index=False).encode('utf-8')

st.download_button(
    label='Descargar CSV con resultados',
    data=csv_data,
    file_name='similitud_resultados.csv',
    mime='text/csv'
)

st.markdown('---')
st.markdown('**Notas:**\n'
            '- Si deseas usar otro archivo .bib, cambia la ruta en la barra lateral.\n'
            '- Para ejecutar localmente: `streamlit run similitud_textual_app.py`\n'
            '- Revisa los paquetes listados al inicio (sentence-transformers descarga modelos la primera vez).')

