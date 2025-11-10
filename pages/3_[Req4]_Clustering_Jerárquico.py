"""
[Req4] Clustering Jerárquico
Interfaz para el Requerimiento 4
"""

import streamlit as st
import sys
from pathlib import Path
from PIL import Image
import pandas as pd
import glob

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

# Configurar logger
from src.utils.logger import get_logger
logger = get_logger(__name__, req_number=4)

st.set_page_config(page_title="[Req4] Clustering Jerárquico", page_icon="🌳", layout="wide")

st.title("🌳 [Req4] Clustering Jerárquico de Documentos")
st.markdown("---")

# Descripción detallada
with st.expander("ℹ️ Acerca de este Requerimiento", expanded=False):
    st.markdown("""
    ## 📋 Descripción del Requerimiento 4
    
    Agrupamiento jerárquico aglomerativo de documentos académicos usando **3 métodos de linkage**:
    
    ### 1️⃣ Single Linkage (Vecino Más Cercano)
    
    **Distancia entre clusters:**
    $$
    d_{\\text{single}}(C_i, C_j) = \\min_{x \\in C_i, y \\in C_j} d(x, y)
    $$
    
    - **Complejidad:** O(n³)
    - **Ventaja:** Detecta formas no convexas
    - **Desventaja:** Sensible a outliers ("chaining effect")
    
    ---
    
    ### 2️⃣ Complete Linkage (Vecino Más Lejano)
    
    **Distancia entre clusters:**
    $$
    d_{\\text{complete}}(C_i, C_j) = \\max_{x \\in C_i, y \\in C_j} d(x, y)
    $$
    
    - **Complejidad:** O(n³)
    - **Ventaja:** Clusters compactos y separados
    - **Desventaja:** Sensible a outliers, clusters esféricos
    
    ---
    
    ### 3️⃣ Ward's Method (Mínima Varianza)
    
    **Minimiza la suma de cuadrados dentro de clusters:**
    $$
    \\Delta(C_i, C_j) = \\sum_{x \\in C_i \\cup C_j} \\|x - \\mu_{ij}\\|^2 - \\sum_{x \\in C_i} \\|x - \\mu_i\\|^2 - \\sum_{x \\in C_j} \\|x - \\mu_j\\|^2
    $$
    
    Donde:
    - $\\mu_i$: centroide del cluster $C_i$
    - $\\mu_{ij}$: centroide del cluster fusionado
    
    **Fórmula de Lance-Williams:**
    $$
    d_{\\text{Ward}}(C_k, C_i \\cup C_j) = \\sqrt{\\frac{(|C_i| + |C_k|) d^2_{ik} + (|C_j| + |C_k|) d^2_{jk} - |C_k| d^2_{ij}}{|C_i| + |C_j| + |C_k|}}
    $$
    
    - **Complejidad:** O(n³)
    - **Ventaja:** Clusters balanceados, interpretación estadística
    - **Desventaja:** Requiere distancia euclidiana
    
    ---
    
    ## 🧮 Vectorización de Documentos
    
    ### Opción A: TF-IDF
    $$
    \\mathbf{v}_d = [\\text{tfidf}(t_1, d), \\text{tfidf}(t_2, d), ..., \\text{tfidf}(t_n, d)]
    $$
    
    - **Dimensionalidad:** Vocabulario completo (~5000-10000)
    - **Ventaja:** Rápido, interpretable
    - **Limitación:** No captura semántica
    
    ### Opción B: Sentence Embeddings
    $$
    \\mathbf{v}_d = \\text{SentenceTransformer}(\\text{title} + \\text{abstract})
    $$
    
    - **Modelo:** all-MiniLM-L6-v2
    - **Dimensionalidad:** 384
    - **Ventaja:** Captura semántica profunda
    - **Limitación:** Más lento
    
    ---
    
    ## 📊 Dendrograma
    
    Visualización jerárquica del proceso de clustering:
    
    - **Eje Y:** Distancia de fusión
    - **Eje X:** Documentos individuales
    - **Ramas:** Estructura de clusters
    - **Altura de fusión:** Disimilitud entre clusters
    
    **Interpretación:**
    - Fusiones bajas: documentos muy similares
    - Fusiones altas: clusters diferenciados
    - Corte horizontal: determina número de clusters
    
    ---
    
    ## ⚙️ Algoritmo Aglomerativo
    
    ```
    1. Inicializar: Cada documento = 1 cluster
    2. Calcular matriz de distancias (n × n)
    3. Mientras n_clusters > 1:
         a. Encontrar par de clusters más cercanos
         b. Fusionar en nuevo cluster
         c. Actualizar distancias (Lance-Williams)
         d. Registrar fusión en dendrograma
    4. Retornar estructura jerárquica
    ```
    
    **Complejidad total:** O(n² log n) con optimizaciones, O(n³) genérico
    """)

st.markdown("---")

# Verificar archivo unificado
unified_file = PROJECT_ROOT / "data/processed/unified_references.bib"

if not unified_file.exists():
    st.error("❌ No se encontró `unified_references.bib`")
    st.info("👉 **Primero ejecuta [Req1] Descarga y Unificación** para obtener las referencias")
    logger.error("unified_references.bib no encontrado")
    st.stop()

# Configuración
st.subheader("⚙️ Configuración del Clustering")

col1, col2, col3 = st.columns(3)

with col1:
    method = st.selectbox(
        "Método de linkage",
        options=['single', 'complete', 'ward'],
        format_func=lambda x: {
            'single': 'Single (Vecino Cercano)',
            'complete': 'Complete (Vecino Lejano)',
            'ward': 'Ward (Mínima Varianza)'
        }[x]
    )

with col2:
    vectorization = st.selectbox(
        "Vectorización",
        options=['tfidf', 'embeddings'],
        format_func=lambda x: {
            'tfidf': 'TF-IDF (rápido)',
            'embeddings': 'Sentence-BERT (preciso)'
        }[x]
    )

with col3:
    max_docs = st.number_input(
        "Máximo de documentos",
        min_value=10,
        max_value=500,
        value=200 if vectorization == 'tfidf' else 100,
        step=10,
        help="Reducir para mayor velocidad"
    )

# Ejecutar clustering
if st.button("🌳 Ejecutar Clustering", type="primary"):
    logger.info(f"Iniciando clustering: method={method}, vectorization={vectorization}, max_docs={max_docs}")
    
    with st.spinner(f"Ejecutando clustering {method.upper()} con {vectorization}..."):
        try:
            from src.requerimiento4 import run_clustering
            
            import io
            from contextlib import redirect_stdout
            
            output = io.StringIO()
            with redirect_stdout(output):
                run_clustering([
                    '--method', vectorization,
                    '--linkage', method,
                    '--max-docs', str(max_docs)
                ])
            
            st.success("✅ Clustering completado")
            logger.info("✅ Clustering completado exitosamente")
            
            with st.expander("📋 Log de ejecución"):
                st.code(output.getvalue())
                
        except Exception as e:
            st.error(f"❌ Error: {e}")
            logger.error(f"Error en clustering: {e}", exc_info=True)
            st.info("Verifica que exista `data/processed/unified_references.bib`")

st.markdown("---")

# Mostrar dendrogramas
st.subheader("📊 Dendrogramas Generados")

clustering_dir = PROJECT_ROOT / "clustering"

if clustering_dir.exists():
    # Buscar dendrogramas
    dendrograms = glob.glob(str(clustering_dir / "*.png"))
    
    if dendrograms:
        # Crear tabs por linkage method
        tabs = st.tabs(["🔗 Single", "🔗 Complete", "🔗 Ward"])
        
        linkage_methods = ['single', 'complete', 'ward']
        
        for tab, linkage in zip(tabs, linkage_methods):
            with tab:
                # Buscar dendrograma para este linkage
                matching = [d for d in dendrograms if linkage in d]
                
                if matching:
                    latest = max(matching)  # Más reciente
                    
                    try:
                        img = Image.open(latest)
                        st.image(img, caption=f"Dendrograma: {linkage.capitalize()} Linkage", use_container_width=True)
                        logger.info(f"Mostrando dendrograma: {latest}")
                    except Exception as e:
                        st.error(f"Error al cargar imagen: {e}")
                        logger.error(f"Error cargando dendrograma: {e}")
                else:
                    st.info(f"⚠️ No hay dendrograma para {linkage}. Ejecuta el clustering primero.")
    else:
        st.info("⚠️ No hay dendrogramas disponibles. Ejecuta el clustering primero.")
        logger.warning("No se encontraron dendrogramas")
else:
    st.warning("⚠️ Directorio de clustering no encontrado")

st.markdown("---")
st.caption("🔬 [Req4] Clustering Jerárquico | Single, Complete, Ward")
