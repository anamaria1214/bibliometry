"""
[Req3] Análisis de Frecuencia de Términos
Interfaz para el Requerimiento 3
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

# Configurar logger
from src.utils.logger import get_logger
logger = get_logger(__name__, req_number=3)

st.set_page_config(page_title="[Req3] Análisis de Frecuencia", page_icon="📈", layout="wide")

st.title("📈 [Req3] Análisis de Frecuencia de Términos")
st.markdown("---")

# Descripción detallada
with st.expander("ℹ️ Acerca de este Requerimiento", expanded=False):
    st.markdown("""
    ## 📋 Descripción del Requerimiento 3
    
    Este módulo realiza **análisis de frecuencia de términos** en la literatura académica usando dos enfoques complementarios:
    
    ### 1️⃣ Conteo Directo de Términos
    
    Identifica palabras clave predefinidas en los documentos.
    
    **Fórmula:**
    $$
    \\text{freq}(t) = \\sum_{d \\in D} \\mathbb{1}_{t \\in d}
    $$
    
    Donde:
    - $t$: término de interés
    - $D$: corpus de documentos
    - $\\mathbb{1}_{t \\in d}$: función indicadora (1 si $t$ está en $d$, 0 en otro caso)
    
    **Términos predefinidos:**
    - Generative AI
    - Large Language Models (LLM)
    - Diffusion Models
    - Transformers
    - GPT
    - BERT
    - Stable Diffusion
    - Y más...
    
    ---
    
    ### 2️⃣ Descubrimiento Algorítmico con TF-IDF
    
    Identifica automáticamente términos relevantes usando **TF-IDF**.
    
    **Fórmula TF-IDF:**
    $$
    \\text{tfidf}(t, d, D) = \\text{tf}(t, d) \\times \\text{idf}(t, D)
    $$
    
    Donde:
    
    **Term Frequency (TF):**
    $$
    \\text{tf}(t, d) = \\frac{f_{t,d}}{\\sum_{t' \\in d} f_{t',d}}
    $$
    
    **Inverse Document Frequency (IDF):**
    $$
    \\text{idf}(t, D) = \\log \\frac{|D|}{|\\{d \\in D : t \\in d\\}|}
    $$
    
    - $f_{t,d}$: frecuencia del término $t$ en documento $d$
    - $|D|$: número total de documentos
    - $|\\{d \\in D : t \\in d\\}|$: número de documentos que contienen $t$
    
    ---
    
    ## 🎯 Metodología
    
    ### Pipeline de Análisis
    
    1. **Preprocesamiento**
       - Parseo de archivos BibTeX
       - Extracción de títulos y abstracts
       - Normalización de texto (lowercase, puntuación)
    
    2. **Tokenización**
       - Separación en palabras individuales
       - Eliminación de stopwords (the, a, an, etc.)
       - Filtrado de tokens muy cortos (<3 caracteres)
    
    3. **Cálculo de Frecuencias**
       - Conteo directo para términos predefinidos
       - TF-IDF para descubrimiento de términos emergentes
       - Ranking por score
    
    4. **Exportación**
       - `category_frequencies.csv`: Conteo directo
       - `auto_discovered_terms.csv`: Top términos TF-IDF
       - Gráficos de barras
    
    ---
    
    ## 📊 Interpretación de Resultados
    
    ### Conteo Directo
    - **Alta frecuencia:** Tema central en el corpus
    - **Baja frecuencia:** Nicho o emergente
    - **Cero:** No mencionado (posible gap de investigación)
    
    ### TF-IDF
    - **Alto TF-IDF:** Término distintivo y relevante
    - **Bajo TF-IDF:** Término común o poco discriminativo
    - **Top-N:** Términos más característicos del corpus
    
    ---
    
    ## 🔧 Parámetros Configurables
    
    - **min_df:** Frecuencia mínima de documentos (default: 2)
    - **max_features:** Número máximo de términos (default: 100)
    - **ngram_range:** Rango de n-gramas (default: (1, 2) para unigramas y bigramas)
    - **stopwords:** Lenguaje (default: 'english')
    
    ---
    
    ## 💡 Aplicaciones
    
    - **Revisión sistemática:** Identificar temas principales
    - **Gap analysis:** Encontrar áreas poco exploradas
    - **Trend analysis:** Detectar términos emergentes
    - **Keyword extraction:** Para indexación y búsqueda
    """)

st.markdown("---")

# Verificar archivo unificado
unified_file = PROJECT_ROOT / "data/processed/unified_references.bib"

if not unified_file.exists():
    st.error("❌ No se encontró `unified_references.bib`")
    st.info("👉 **Primero ejecuta [Req1] Descarga y Unificación** para obtener las referencias")
    logger.error("unified_references.bib no encontrado")
    st.stop()

# Botón para ejecutar análisis
col1, col2 = st.columns([2, 1])

with col1:
    if st.button("🔍 Ejecutar Análisis de Frecuencia", type="primary"):
        logger.info("Iniciando análisis de frecuencia...")
        
        with st.spinner("Analizando términos en la base de datos..."):
            try:
                from src.requerimiento3 import run_analysis
                
                import io
                from contextlib import redirect_stdout
                
                output = io.StringIO()
                with redirect_stdout(output):
                    run_analysis()
                
                st.success("✅ Análisis completado")
                logger.info("✅ Análisis de frecuencia completado exitosamente")
                
                with st.expander("📋 Log de ejecución"):
                    st.code(output.getvalue())
                    
            except Exception as e:
                st.error(f"❌ Error: {e}")
                logger.error(f"Error en análisis: {e}", exc_info=True)
                st.info("Verifica que exista `data/processed/unified_references.bib`")

with col2:
    st.info("**Datos requeridos:**\n\n`unified_references.bib`")

st.markdown("---")

# Mostrar resultados
analysis_dir = PROJECT_ROOT / "data/analysis"
category_file = analysis_dir / "category_frequencies.csv"
terms_file = analysis_dir / "auto_discovered_terms.csv"

if category_file.exists() or terms_file.exists():
    st.subheader("📊 Resultados del Análisis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📌 Conteo Directo")
        if category_file.exists():
            try:
                df_cat = pd.read_csv(category_file)
                
                # Verificar columnas disponibles
                if 'total_occurrences' in df_cat.columns and 'seed_term' in df_cat.columns:
                    # Métricas
                    total_terms = len(df_cat)
                    found_terms = len(df_cat[df_cat['total_occurrences'] > 0])
                    st.metric("Términos encontrados", f"{found_terms}/{total_terms}")
                    
                    # Preparar datos para gráfico (agrupar por seed_term)
                    df_grouped = df_cat.groupby('seed_term')['total_occurrences'].sum().sort_values(ascending=False)
                    
                    # Gráfico
                    st.bar_chart(df_grouped)
                    
                    # Tabla
                    with st.expander("📋 Ver tabla completa"):
                        st.dataframe(df_cat, use_container_width=True)
                        
                        st.download_button(
                            "📥 Descargar CSV",
                            df_cat.to_csv(index=False),
                            "category_frequencies.csv",
                            "text/csv"
                        )
                    
                    logger.info(f"Términos predefinidos encontrados: {found_terms}/{total_terms}")
                else:
                    st.warning("⚠️ Formato de CSV no reconocido")
                    st.dataframe(df_cat.head(), use_container_width=True)
                    logger.warning(f"Columnas disponibles: {df_cat.columns.tolist()}")
                    
            except Exception as e:
                st.error(f"Error al cargar: {e}")
                logger.error(f"Error cargando category_frequencies: {e}", exc_info=True)
        else:
            st.info("⚠️ No hay datos de conteo directo")
    
    with col2:
        st.markdown("### 🔎 Descubrimiento TF-IDF")
        if terms_file.exists():
            try:
                df_terms = pd.read_csv(terms_file)
                
                # Verificar columnas disponibles
                if 'tfidf_sum' in df_terms.columns and 'term' in df_terms.columns:
                    # Métricas
                    st.metric("Términos descubiertos", len(df_terms))
                    
                    # Gráfico (top 20)
                    top_terms = df_terms.head(20)
                    st.bar_chart(top_terms.set_index('term')['tfidf_sum'])
                    
                    # Tabla
                    with st.expander("📋 Ver tabla completa"):
                        st.dataframe(df_terms, use_container_width=True)
                        
                        st.download_button(
                            "📥 Descargar CSV",
                            df_terms.to_csv(index=False),
                            "auto_discovered_terms.csv",
                            "text/csv"
                        )
                    
                    logger.info(f"Términos TF-IDF extraídos: {len(df_terms)}")
                else:
                    st.warning("⚠️ Formato de CSV no reconocido")
                    st.dataframe(df_terms.head(), use_container_width=True)
                    logger.warning(f"Columnas disponibles: {df_terms.columns.tolist()}")
                    
            except Exception as e:
                st.error(f"Error al cargar: {e}")
                logger.error(f"Error cargando auto_discovered_terms: {e}", exc_info=True)
        else:
            st.info("⚠️ No hay datos de TF-IDF")
else:
    st.info("⚠️ No hay resultados disponibles. Ejecuta el análisis primero.")
    logger.warning("No se encontraron archivos de resultados")

st.markdown("---")
st.caption("🔬 [Req3] Análisis de Frecuencia | Conteo Directo + TF-IDF")
