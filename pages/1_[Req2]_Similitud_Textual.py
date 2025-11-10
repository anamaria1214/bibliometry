"""
[Req2] Similitud Textual - 6 Algoritmos
Interfaz para el Requerimiento 2
"""

import streamlit as st
import sys
from pathlib import Path
import importlib.util

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

# Configurar logger
from src.utils.logger import get_logger
logger = get_logger(__name__, req_number=2)

st.set_page_config(page_title="[Req2] Similitud Textual", page_icon="📊", layout="wide")

st.title("📊 [Req2] Similitud Textual - 6 Algoritmos Comparativos")
st.markdown("---")

# Descripción detallada del requerimiento
with st.expander("ℹ️ Acerca de este Requerimiento", expanded=False):
    st.markdown("""
    ## 📋 Descripción del Requerimiento 2
    
    Este módulo implementa **6 algoritmos de similitud textual** para comparar documentos académicos:
    
    ### 1️⃣ Levenshtein Distance (Distancia de Edición)
    
    Mide el número mínimo de operaciones (inserción, eliminación, sustitución) para transformar un string en otro.
    
    **Fórmula:**
    $$
    \\text{lev}(a, b) = \\begin{cases}
    |a| & \\text{si } |b| = 0 \\\\
    |b| & \\text{si } |a| = 0 \\\\
    \\min \\begin{cases}
    \\text{lev}(a[1:], b) + 1 \\\\
    \\text{lev}(a, b[1:]) + 1 \\\\
    \\text{lev}(a[1:], b[1:]) + [a[0] \\neq b[0]]
    \\end{cases} & \\text{en otro caso}
    \\end{cases}
    $$
    
    **Normalización:** `sim = 1 - (lev / max(len(a), len(b)))`
    
    - **Complejidad:** O(n × m)
    - **Uso:** Detección de typos, corrección ortográfica
    
    ---
    
    ### 2️⃣ Jaccard Similarity (Índice de Jaccard)
    
    Mide la similitud entre conjuntos de palabras.
    
    **Fórmula:**
    $$
    J(A, B) = \\frac{|A \\cap B|}{|A \\cup B|} = \\frac{|A \\cap B|}{|A| + |B| - |A \\cap B|}
    $$
    
    Donde $A$ y $B$ son conjuntos de tokens (palabras únicas).
    
    - **Rango:** [0, 1]
    - **Ventaja:** Simple y eficiente
    - **Limitación:** Ignora frecuencias y orden
    
    ---
    
    ### 3️⃣ Cosine Similarity + TF-IDF
    
    Calcula el coseno del ángulo entre vectores TF-IDF.
    
    **TF-IDF:**
    $$
    \\text{tfidf}(t, d) = \\text{tf}(t, d) \\times \\log\\left(\\frac{N}{\\text{df}(t)}\\right)
    $$
    
    **Similitud Coseno:**
    $$
    \\cos(\\theta) = \\frac{\\mathbf{A} \\cdot \\mathbf{B}}{\\|\\mathbf{A}\\| \\|\\mathbf{B}\\|} = \\frac{\\sum_{i=1}^{n} A_i B_i}{\\sqrt{\\sum_{i=1}^{n} A_i^2} \\sqrt{\\sum_{i=1}^{n} B_i^2}}
    $$
    
    - **tf(t, d):** Frecuencia del término en el documento
    - **df(t):** Número de documentos que contienen el término
    - **N:** Total de documentos
    - **Rango:** [0, 1]
    
    ---
    
    ### 4️⃣ Euclidean Distance (Distancia Euclidiana)
    
    Distancia geométrica en el espacio vectorial TF-IDF.
    
    **Fórmula:**
    $$
    d(\\mathbf{A}, \\mathbf{B}) = \\sqrt{\\sum_{i=1}^{n} (A_i - B_i)^2}
    $$
    
    **Normalización a similitud:**
    $$
    \\text{sim} = \\frac{1}{1 + d}
    $$
    
    - **Ventaja:** Intuición geométrica clara
    - **Limitación:** Sensible a la magnitud de los vectores
    
    ---
    
    ### 5️⃣ Sentence-BERT (Transformers)
    
    Embeddings contextuales usando **all-MiniLM-L6-v2**.
    
    **Arquitectura:**
    - Base: MiniLM (destilado de BERT)
    - Capas: 6 transformer layers
    - Dimensiones: 384
    - Pooling: Mean pooling
    
    **Similitud:**
    $$
    \\text{sim} = \\cos(\\text{emb}_1, \\text{emb}_2)
    $$
    
    - **Ventaja:** Captura semántica profunda, maneja sinónimos y parafraseo
    - **F1 Score (STSb):** ~82%
    
    ---
    
    ### 6️⃣ Word2Vec Averaging
    
    Embeddings pre-entrenados con promedio de vectores de palabras.
    
    **Proceso:**
    1. Tokenizar documento: $[w_1, w_2, ..., w_n]$
    2. Obtener embeddings: $[\\mathbf{v}_1, \\mathbf{v}_2, ..., \\mathbf{v}_n]$
    3. Promediar:
    $$
    \\mathbf{d} = \\frac{1}{n} \\sum_{i=1}^{n} \\mathbf{v}_i
    $$
    4. Similitud coseno entre promedios
    
    - **Modelo:** Google News 300d
    - **Vocabulario:** 3M palabras
    - **Limitación:** Pérdida de orden sintáctico
    
    ---
    
    ## 🎯 Casos de Uso
    
    | Algoritmo | Mejor para | Velocidad | Precisión |
    |-----------|-----------|-----------|-----------|
    | Levenshtein | Textos cortos, typos | ⚡⚡ | ⭐⭐ |
    | Jaccard | Keywords, tags | ⚡⚡⚡ | ⭐⭐⭐ |
    | TF-IDF + Coseno | Búsqueda documental | ⚡⚡ | ⭐⭐⭐⭐ |
    | Euclidiana | Distancia absoluta | ⚡⚡ | ⭐⭐⭐ |
    | Sentence-BERT | Semántica profunda | ⚡ | ⭐⭐⭐⭐⭐ |
    | Word2Vec | Balance speed/quality | ⚡⚡ | ⭐⭐⭐⭐ |
    """)

st.markdown("---")

# Verificar archivo unificado
unified_file = PROJECT_ROOT / "data/processed/unified_references.bib"

if not unified_file.exists():
    st.error("❌ No se encontró `unified_references.bib`")
    st.info("👉 **Primero ejecuta [Req1] Descarga y Unificación** para obtener las referencias")
    logger.error("unified_references.bib no encontrado")
    st.stop()

logger.info("Cargando módulo de similitud textual...")

# Cargar el módulo de similitud usando importlib
module_path = PROJECT_ROOT / "src" / "requerimiento2" / "similitud_textual_app.py"

if not module_path.exists():
    st.error(f"❌ No se encontró el módulo: {module_path}")
    logger.error(f"Módulo no encontrado: {module_path}")
    st.stop()

# Importar dinámicamente
spec = importlib.util.spec_from_file_location("similitud_module", module_path)
similitud_module = importlib.util.module_from_spec(spec)

try:
    spec.loader.exec_module(similitud_module)
    logger.info("✅ Módulo de similitud cargado correctamente")
except Exception as e:
    st.error(f"❌ Error al cargar el módulo: {e}")
    logger.error(f"Error al cargar módulo: {e}", exc_info=True)
    st.stop()
