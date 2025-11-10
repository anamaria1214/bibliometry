"""
[Req7] Sistema de Recomendación Híbrido
Interfaz para el Requerimiento 7
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

# Configurar logger
from src.utils.logger import get_logger
logger = get_logger(__name__, req_number=7)

st.set_page_config(page_title="[Req7] Recomendador", page_icon="🤖", layout="wide")

st.title("🤖 [Req7] Sistema de Recomendación Híbrido")
st.markdown("---")

# Descripción detallada
with st.expander("ℹ️ Acerca de este Requerimiento", expanded=False):
    st.markdown("""
    ## 📋 Descripción del Requerimiento 7
    
    Sistema de recomendación híbrido que combina **similitud semántica** y **similitud de keywords**.
    
    ### 🧠 Similitud Semántica (Sentence-BERT)
    
    **Modelo:** all-MiniLM-L6-v2
    - **Arquitectura:** MiniLM (BERT destilado)
    - **Capas:** 6 transformer layers
    - **Dimensiones:** 384
    - **Pooling:** Mean pooling
    
    **Embedding de documento:**
    $$
    \\mathbf{e}_d = \\text{SentenceTransformer}(\\text{title}_d + \\text{abstract}_d)
    $$
    
    **Similitud coseno:**
    $$
    \\cos(\\mathbf{e}_i, \\mathbf{e}_j) = \\frac{\\mathbf{e}_i \\cdot \\mathbf{e}_j}{\\|\\mathbf{e}_i\\| \\|\\mathbf{e}_j\\|}
    $$
    
    **Propiedades:**
    - Captura parafraseo y sinónimos
    - Sensible al contexto semántico
    - F1 Score (STSb benchmark): ~82%
    
    ---
    
    ### 🔑 Similitud de Keywords (Jaccard)
    
    **Extracción de keywords:**
    1. Tokenizar: $\\text{text} \\rightarrow [w_1, w_2, ..., w_n]$
    2. Filtrar stopwords: $\\{\\text{the, a, an, is, ...}\\}$
    3. Filtrar longitud: $|w| \\geq 3$
    4. Calcular frecuencias: $f_w = \\sum_{d} \\mathbb{1}_{w \\in d}$
    5. Seleccionar top-K: $K = \\{w_1, ..., w_{20}\\}$
    
    **Índice de Jaccard:**
    $$
    J(K_i, K_j) = \\frac{|K_i \\cap K_j|}{|K_i \\cup K_j|}
    $$
    
    **Propiedades:**
    - Rango: [0, 1]
    - Rápido: O(|K|)
    - Interpretable: términos compartidos
    
    ---
    
    ### ⚖️ Combinación Híbrida
    
    **Score final:**
    $$
    S_{\\text{total}}(d_i, d_j) = \\alpha \\cdot S_{\\text{semantic}}(d_i, d_j) + \\beta \\cdot S_{\\text{keyword}}(d_i, d_j)
    $$
    
    Donde:
    - $\\alpha + \\beta = 1$ (suma a 1)
    - $\\alpha = 0.7$ (default): peso semántico
    - $\\beta = 0.3$ (default): peso keywords
    
    **Justificación de pesos:**
    - **Semántico (70%):** Captura similitud profunda, crítico para recomendaciones de calidad
    - **Keywords (30%):** Añade precisión léxica, útil para términos técnicos
    
    ---
    
    ## 🎯 Algoritmo de Recomendación
    
    ```python
    def recommend(base_article, top_n=5, alpha=0.7, beta=0.3):
        # 1. Extraer keywords
        base_keywords = extract_top_keywords(base_article.text, k=20)
        
        # 2. Generar embeddings
        base_embedding = model.encode(base_article.text)
        
        # 3. Para cada artículo candidato:
        scores = []
        for candidate in corpus:
            # Similitud semántica
            sem_sim = cosine_similarity(
                base_embedding, 
                model.encode(candidate.text)
            )
            
            # Similitud de keywords
            cand_keywords = extract_top_keywords(candidate.text, k=20)
            key_sim = jaccard(base_keywords, cand_keywords)
            
            # Combinar
            hybrid_score = alpha * sem_sim + beta * key_sim
            scores.append((candidate, hybrid_score))
        
        # 4. Ordenar y retornar top-N
        return sorted(scores, key=lambda x: x[1], reverse=True)[:top_n]
    ```
    
    ---
    
    ## 📊 Métricas de Evaluación
    
    - **Precision@K:** Proporción de recomendaciones relevantes en top-K
    - **Recall@K:** Proporción de artículos relevantes recuperados
    - **NDCG:** Descuento de posición en ranking
    - **Diversity:** Variedad temática en recomendaciones
    
    ---
    
    ## 💡 Casos de Uso
    
    1. **Literatura relacionada:** Encontrar papers similares para revisión
    2. **Expansión de búsqueda:** Descubrir nuevos ángulos de investigación
    3. **Gap analysis:** Identificar áreas poco exploradas
    4. **Colaboración:** Conectar investigadores con intereses afines
    """)

st.markdown("---")

# Verificar datos
bib_file = PROJECT_ROOT / "data/processed/unified_references.bib"
metadata_file = PROJECT_ROOT / "data/analysis/metadata.csv"

if not bib_file.exists():
    st.error("❌ No se encontró `unified_references.bib`")
    st.info("👉 **Primero ejecuta [Req1] Descarga y Unificación** para obtener las referencias")
    logger.error("unified_references.bib no encontrado")
    st.stop()

if not metadata_file.exists():
    st.warning("⚠️ No se encontró `metadata.csv`")
    st.info("👉 **Primero ejecuta [Req5] Visualizaciones → 'Extraer Metadata'** para generar el archivo necesario")
    logger.warning("metadata.csv no encontrado")
    articles_available = False
else:
    df_metadata = pd.read_csv(metadata_file)
    articles_available = True
    logger.info(f"Metadata cargada: {len(df_metadata)} artículos")

st.markdown("---")

# Selector de artículo
st.subheader("📝 Selecciona un Artículo Base")

col1, col2 = st.columns([2, 1])

with col1:
    if articles_available and len(df_metadata) > 0:
        article_options = []
        for idx, row in df_metadata.iterrows():
            title = row.get('title', 'Sin título')[:80]
            year = row.get('year', 'N/A')
            article_options.append(f"{idx}: {title}... ({year})")
        
        selected_article = st.selectbox(
            "Artículo de referencia",
            range(len(article_options)),
            format_func=lambda x: article_options[x]
        )
    else:
        selected_article = 0

with col2:
    num_recommendations = st.number_input(
        "Núm. recomendaciones",
        min_value=1,
        max_value=20,
        value=5
    )

# Configuración avanzada
with st.expander("⚙️ Configuración Avanzada"):
    col1, col2 = st.columns(2)
    
    with col1:
        semantic_weight = st.slider(
            "Peso Semántico",
            0.0, 1.0, 0.7, 0.05
        )
    
    with col2:
        keyword_weight = 1.0 - semantic_weight
        st.metric("Peso Keywords", f"{keyword_weight:.2f}")

# Obtener recomendaciones
if st.button("🔍 Obtener Recomendaciones", type="primary"):
    logger.info(f"Obteniendo recomendaciones para artículo {selected_article}")
    
    if not articles_available:
        st.error("❌ No hay metadata disponible")
    else:
        with st.spinner("Calculando similitudes..."):
            try:
                from src.requerimiento7 import get_recommendations
                
                recommendations = get_recommendations(
                    article_index=selected_article,
                    num_recommendations=num_recommendations,
                    semantic_weight=semantic_weight,
                    keyword_weight=keyword_weight
                )
                
                st.success(f"✅ {len(recommendations)} recomendaciones")
                logger.info(f"✅ {len(recommendations)} recomendaciones generadas")
                
                # Artículo base
                st.markdown("---")
                st.subheader("📄 Artículo Base")
                
                base_article = df_metadata.iloc[selected_article]
                st.markdown(f"**{base_article.get('title', 'Sin título')}**")
                st.caption(f"👤 {base_article.get('author', 'Desconocido')} | 📅 {base_article.get('year', 'N/A')}")
                
                # Recomendaciones
                st.markdown("---")
                st.subheader("🎯 Recomendaciones")
                
                for i, rec in enumerate(recommendations, 1):
                    col1, col2, col3 = st.columns([0.5, 6, 2])
                    
                    with col1:
                        st.markdown(f"### {i}")
                    
                    with col2:
                        st.markdown(f"**{rec['title'][:100]}...**")
                        st.caption(f"👤 {rec['author']} | 📅 {rec['year']}")
                    
                    with col3:
                        st.metric("Score", f"{rec['hybrid_score']:.3f}")
                        with st.popover("📊"):
                            st.write(f"🧠 Sem: {rec['semantic_score']:.3f}")
                            st.write(f"🔑 Key: {rec['keyword_score']:.3f}")
                    
                    st.markdown("---")
                
                logger.info("Recomendaciones mostradas correctamente")
                
            except Exception as e:
                st.error(f"❌ Error: {e}")
                logger.error(f"Error: {e}", exc_info=True)

st.markdown("---")
st.caption("🔬 [Req7] Recomendador | Sentence-BERT 70% + Jaccard 30%")
