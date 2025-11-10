"""
[Req5] Visualizaciones Analíticas
Interfaz para el Requerimiento 5
"""

import streamlit as st
import sys
from pathlib import Path
from PIL import Image
import glob
import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

# Configurar logger
from src.utils.logger import get_logger
logger = get_logger(__name__, req_number=5)

st.set_page_config(page_title="[Req5] Visualizaciones", page_icon="🗺️", layout="wide")

st.title("🗺️ [Req5] Visualizaciones Analíticas")
st.markdown("---")

# Descripción detallada
with st.expander("ℹ️ Acerca de este Requerimiento", expanded=False):
    st.markdown("""
    ## 📋 Descripción del Requerimiento 5
    
    Generación de visualizaciones para análisis exploratorio de datos bibliométricos.
    
    ### 1️⃣ Mapa de Calor Geográfico
    
    **Fórmula de densidad:**
    $$
    \\text{density}(\\text{country}) = \\frac{\\text{count}(\\text{papers})}{\\text{area}(\\text{country})}
    $$
    
    **Implementación:** Plotly choropleth + Geopandas
    
    ---
    
    ### 2️⃣ Nube de Palabras
    
    **Fórmula de tamaño:**
    $$
    \\text{size}(w) \\propto \\sqrt{\\text{freq}(w)}
    $$
    
    **Filtrado:** Stopwords + min length ≥ 3
    
    ---
    
    ### 3️⃣ Línea Temporal
    
    **Series temporales:**
    $$
    y(t) = \\sum_{d \\in D} \\mathbb{1}_{\\text{year}(d) = t}
    $$
    
    **Tasa de crecimiento:**
    $$
    \\text{growth}(t) = \\frac{y(t) - y(t-1)}{y(t-1)} \\times 100\\%
    $$
    """)

st.markdown("---")

# Verificar archivo unificado
unified_file = PROJECT_ROOT / "data/processed/unified_references.bib"

if not unified_file.exists():
    st.error("❌ No se encontró `unified_references.bib`")
    st.info("👉 **Primero ejecuta [Req1] Descarga y Unificación** para obtener las referencias")
    logger.error("unified_references.bib no encontrado")
    st.stop()

# Botones
col1, col2 = st.columns([3, 1])

with col1:
    if st.button("🎨 Generar Visualizaciones", type="primary"):
        logger.info("Generando visualizaciones...")
        
        with st.spinner("Generando..."):
            try:
                from src.requerimiento5 import run_visualizations
                import io
                from contextlib import redirect_stdout
                
                output = io.StringIO()
                with redirect_stdout(output):
                    run_visualizations()
                
                st.success("✅ Generadas")
                logger.info("✅ Visualizaciones generadas")
                
                with st.expander("📋 Log"):
                    st.code(output.getvalue())
                    
            except Exception as e:
                st.error(f"❌ Error: {e}")
                logger.error(f"Error: {e}", exc_info=True)

with col2:
    metadata_file = PROJECT_ROOT / "data/analysis/metadata.csv"
    if not metadata_file.exists():
        if st.button("📋 Extraer Metadata"):
            logger.info("Extrayendo metadata...")
            try:
                from src.requerimiento5 import extract_metadata
                extract_metadata.main()
                st.success("✅ Extraída")
                logger.info("✅ Metadata extraída")
            except Exception as e:
                st.error(f"❌ {e}")

st.markdown("---")

# Mostrar visualizaciones
analysis_dir = PROJECT_ROOT / "data/analysis"

if analysis_dir.exists():
    viz_files = {'heatmap': None, 'wordcloud': None, 'timeline': None}
    
    for viz_type in viz_files.keys():
        pattern = str(analysis_dir / f"*{viz_type}*.png")
        files = sorted(glob.glob(pattern), reverse=True)
        if files:
            viz_files[viz_type] = files[0]
    
    tabs = st.tabs(["🌍 Mapa de Calor", "☁️ Nube de Palabras", "📅 Timeline"])
    
    with tabs[0]:
        if viz_files['heatmap']:
            img = Image.open(viz_files['heatmap'])
            st.image(img, use_container_width=True)
            logger.info("Mostrando heatmap")
        else:
            st.info("⚠️ No disponible")
    
    with tabs[1]:
        if viz_files['wordcloud']:
            img = Image.open(viz_files['wordcloud'])
            st.image(img, use_container_width=True)
            logger.info("Mostrando wordcloud")
        else:
            st.info("⚠️ No disponible")
    
    with tabs[2]:
        if viz_files['timeline']:
            img = Image.open(viz_files['timeline'])
            st.image(img, use_container_width=True)
            logger.info("Mostrando timeline")
        else:
            st.info("⚠️ No disponible")

st.markdown("---")
st.caption("🔬 [Req5] Visualizaciones | Heatmap, Wordcloud, Timeline")
