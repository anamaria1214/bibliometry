#!/usr/bin/env python3
"""
Dashboard Principal - Sistema de Análisis Bibliométrico
Generative Artificial Intelligence Research

Este es el punto de entrada para el dashboard integrado con Streamlit.
Proporciona navegación entre todos los módulos de análisis.
"""

import streamlit as st
from pathlib import Path

# Configuración de la página
st.set_page_config(
    page_title="Análisis Bibliométrico - IA Generativa",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos personalizados
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
        border-bottom: 3px solid #1f77b4;
        margin-bottom: 2rem;
    }
    .module-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 5px solid #1f77b4;
    }
    .module-title {
        font-size: 1.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .module-desc {
        color: #555;
        font-size: 1rem;
        line-height: 1.5;
    }
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.875rem;
        font-weight: bold;
        margin-left: 0.5rem;
    }
    .status-complete {
        background-color: #28a745;
        color: white;
    }
    .status-dev {
        background-color: #ffc107;
        color: #333;
    }
    </style>
""", unsafe_allow_html=True)

# Header principal
st.markdown('<div class="main-header">📚 Sistema de Análisis Bibliométrico</div>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #666; font-size: 1.1rem;">Generative Artificial Intelligence Research</p>', unsafe_allow_html=True)

# Sidebar con información
with st.sidebar:
    st.image("https://raw.githubusercontent.com/streamlit/streamlit/develop/docs/_static/logo.png", width=100)
    st.markdown("### 🎯 Navegación")
    st.info("👈 Usa el menú de la izquierda para acceder a cada módulo de análisis")
    
    st.markdown("---")
    st.markdown("### 📊 Estado del Sistema")
    
    # Verificar archivos de datos
    PROJECT_ROOT = Path(__file__).parent
    unified_bib = PROJECT_ROOT / "data/processed/unified_references.bib"
    
    if unified_bib.exists():
        st.success("✅ Datos unificados disponibles")
        # Contar entradas
        try:
            with open(unified_bib, 'r', encoding='utf-8') as f:
                content = f.read()
                entries_count = content.count('@')
            st.metric("Artículos procesados", entries_count)
        except:
            pass
    else:
        st.warning("⚠️ Datos no encontrados")
        st.info("Ejecuta el Requerimiento 1 para descargar datos")
    
    st.markdown("---")
    st.markdown("### ℹ️ Información")
    st.caption("Sistema desarrollado para análisis bibliométrico de publicaciones sobre IA Generativa")
    st.caption("Versión: 1.0.0")

# Contenido principal - Home
st.markdown("## 🏠 Bienvenido al Dashboard")

st.markdown("""
Este sistema integra múltiples herramientas de análisis bibliométrico para estudiar 
publicaciones académicas sobre **Inteligencia Artificial Generativa**.

### 📋 Módulos Disponibles

Usa el panel lateral para navegar entre los diferentes módulos de análisis:
""")

# Módulo 1 (Req1)
st.markdown("""
<div class="module-card">
    <div class="module-title">📥 [Req1] Descarga y Unificación</div>
    <div class="module-desc">
        <b>⚠️ PASO INICIAL OBLIGATORIO</b> - Descarga automática de artículos desde múltiples fuentes académicas:
        <ul>
            <li><b>Semantic Scholar API</b>: Descarga multidisciplinaria con reintentos exponenciales</li>
            <li><b>IEEE Xplore Scraper</b>: Web scraping con Playwright</li>
            <li><b>Unificación BibTeX</b>: Deduplicación por DOI/título (Levenshtein < 0.1)</li>
        </ul>
        <i>Salida:</i> <code>data/processed/unified_references.bib</code><br>
        <i>Estado:</i> <span class="status-badge status-complete">✅ Operativo</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Módulo 2 (Req2)
st.markdown("""
<div class="module-card">
    <div class="module-title">📊 [Req2] Similitud Textual</div>
    <div class="module-desc">
        <i>Prerequisito:</i> [Req1] <code>unified_references.bib</code><br><br>
        Análisis de similitud entre documentos con 6 algoritmos:
        <ul>
            <li><b>Levenshtein</b>: Distancia de edición normalizada (caracteres)</li>
            <li><b>Jaccard</b>: Similitud de conjuntos (tokens únicos)</li>
            <li><b>Coseno TF-IDF</b>: Vectorización con frecuencia inversa</li>
            <li><b>Euclidiana</b>: Distancia normalizada en espacio vectorial</li>
            <li><b>Sentence-BERT</b>: Embeddings semánticos profundos (384-dim)</li>
            <li><b>Word2Vec</b>: Embeddings contextuales promediados</li>
        </ul>
        <i>Estado:</i> <span class="status-badge status-complete">✅ Operativo</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Módulo 3 (Req3)
st.markdown("""
<div class="module-card">
    <div class="module-title">📈 [Req3] Análisis de Frecuencia</div>
    <div class="module-desc">
        <i>Prerequisito:</i> [Req1] <code>unified_references.bib</code><br><br>
        Análisis de términos clave en abstracts con doble enfoque:
        <ul>
            <li><b>Conteo directo</b>: Términos predefinidos del dominio (17 categorías)</li>
            <li><b>Descubrimiento TF-IDF</b>: Extracción algorítmica de términos relevantes</li>
            <li><b>Métricas de precisión</b>: Evaluación de calidad (manual vs automático)</li>
        </ul>
        <i>Salida:</i> <code>category_frequencies.csv</code>, <code>auto_discovered_terms.csv</code><br>
        <i>Estado:</i> <span class="status-badge status-complete">✅ Operativo</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Módulo 4 (Req4)
st.markdown("""
<div class="module-card">
    <div class="module-title">🌳 [Req4] Clustering Jerárquico</div>
    <div class="module-desc">
        <i>Prerequisito:</i> [Req1] <code>unified_references.bib</code><br><br>
        Agrupamiento jerárquico aglomerativo con múltiples métodos de linkage:
        <ul>
            <li><b>Single Linkage</b>: Distancia mínima entre clusters (cadenas largas)</li>
            <li><b>Complete Linkage</b>: Distancia máxima (clusters compactos)</li>
            <li><b>Ward</b>: Minimización de varianza intra-cluster (balanced)</li>
        </ul>
        Vectorización: TF-IDF (disperso) o Sentence-BERT (denso 384-dim).<br>
        <i>Estado:</i> <span class="status-badge status-complete">✅ Operativo</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Módulo 5 (Req5)
st.markdown("""
<div class="module-card">
    <div class="module-title">🗺️ [Req5] Visualizaciones</div>
    <div class="module-desc">
        <i>Prerequisito:</i> [Req1] <code>unified_references.bib</code><br><br>
        Generación de visualizaciones analíticas interactivas:
        <ul>
            <li><b>Mapa de calor geográfico</b>: Distribución por país (Folium)</li>
            <li><b>Nube de palabras</b>: Términos más frecuentes (WordCloud)</li>
            <li><b>Línea temporal</b>: Evolución anual de publicaciones (Plotly)</li>
        </ul>
        <i>Salida:</i> <code>metadata.csv</code> (necesario para Req7)<br>
        <i>Estado:</i> <span class="status-badge status-complete">✅ Operativo</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Módulo 7 (Req7)
st.markdown("""
<div class="module-card">
    <div class="module-title">🤖 [Req7] Sistema de Recomendación</div>
    <div class="module-desc">
        <i>Prerequisitos:</i> [Req1] <code>unified_references.bib</code> + [Req5] <code>metadata.csv</code><br><br>
        Motor híbrido de recomendación de artículos similares:
        <ul>
            <li><b>Similitud semántica (70%)</b>: Embeddings Sentence-BERT (384-dim)</li>
            <li><b>Solapamiento de keywords (30%)</b>: Índice de Jaccard</li>
            <li><b>Justificación explicable</b>: Métricas individuales y keywords comunes</li>
        </ul>
        Fórmula: <code>score_final = 0.7 × sim_semántica + 0.3 × jaccard_keywords</code><br>
        <i>Estado:</i> <span class="status-badge status-complete">✅ Operativo</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Instrucciones de uso
st.markdown("---")
st.markdown("## 🚀 Guía de Uso")

st.info("📌 **Orden de Ejecución Recomendado:** Req1 → Req2/3/4 → Req5 → Req7")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    ### 1️⃣ Descarga Inicial
    
    **[Req1] Descarga y Unificación**
    - Semantic Scholar API
    - IEEE Xplore Scraper  
    - Unificación BibTeX
    
    ➡️ Genera: `unified_references.bib`
    
    🔗 Página: **[Req1] Descarga y Unificación**
    """)

with col2:
    st.markdown("""
    ### 2️⃣ Análisis
    
    **[Req2] Similitud Textual**
    **[Req3] Análisis de Frecuencia**
    **[Req4] Clustering Jerárquico**
    
    ➡️ Generan: CSV de análisis
    
    🔗 Páginas: **[Req2/3/4]**
    """)

with col3:
    st.markdown("""
    ### 3️⃣ Visualización
    
    **[Req5] Visualizaciones**
    - Extrae metadata (⚠️ obligatorio)
    - Genera mapas/gráficos
    
    ➡️ Genera: `metadata.csv`
    
    **[Req7] Recomendador**
    - Usa metadata.csv
    
    🔗 Páginas: **[Req5] → [Req7]**
    """)

st.markdown("---")
st.markdown("### ⚠️ Dependencias Críticas")

col_a, col_b = st.columns(2)

with col_a:
    st.warning("""
    **Todos los módulos** requieren ejecutar primero:
    
    🔹 **[Req1] Descarga y Unificación**
    
    Si ves error "unified_references.bib no encontrado", vuelve a [Req1].
    """)

with col_b:
    st.warning("""
    **[Req7] Recomendador** requiere adicionalmente:
    
    🔹 **[Req5] Visualizaciones → Extraer Metadata**
    
    Si ves error "metadata.csv no encontrado", ejecuta [Req5] primero.
    """)

st.markdown("---")

# Footer
st.markdown("""
<div style="text-align: center; color: #999; padding: 2rem 0; border-top: 1px solid #ddd; margin-top: 2rem;">
    <p>📚 Sistema de Análisis Bibliométrico | Desarrollado con Streamlit</p>
    <p>🔗 <a href="https://github.com/anamaria1214/bibliometry" target="_blank">Repositorio GitHub</a></p>
</div>
""", unsafe_allow_html=True)
