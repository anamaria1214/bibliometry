"""
[Req1] Automatización de Descarga y Unificación
Interfaz para el Requerimiento 1
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

# Configurar logger
from src.utils.logger import get_logger
logger = get_logger(__name__, req_number=1)

st.set_page_config(page_title="[Req1] Descarga y Unificación", page_icon="📥", layout="wide")

st.title("📥 [Req1] Automatización de Descarga y Unificación")
st.markdown("---")

# Descripción detallada
with st.expander("ℹ️ Acerca de este Requerimiento", expanded=False):
    st.markdown("""
    ## 📋 Descripción del Requerimiento 1
    
    Automatización de descarga de artículos desde múltiples fuentes académicas y unificación de registros BibTeX.
    
    ### 1️⃣ Semantic Scholar API
    
    **Endpoint:**
    ```
    GET https://api.semanticscholar.org/graph/v1/paper/search
    ```
    
    **Parámetros:**
    - `query`: Términos de búsqueda (e.g., "Generative AI")
    - `fields`: title, authors, year, abstract, citationCount, publicationDate
    - `limit`: Resultados por página (max 100)
    - `offset`: Paginación
    
    **Retry Logic con Exponential Backoff:**
    $$
    \\text{wait\\_time} = 2^{\\text{attempt}} + \\text{random}(0, 1)
    $$
    
    **Manejo de errores:**
    - **429 (Rate Limit):** Backoff exponencial, max 5 reintentos
    - **5xx (Server Error):** Reintento con backoff
    - **4xx (Client Error):** Abort sin reintento
    
    ---
    
    ### 2️⃣ IEEE Xplore Scraper
    
    **Tecnología:** Playwright (Chromium headless)
    
    **Proceso:**
    1. Navegar a IEEE Xplore search
    2. Inyectar query: "Generative Artificial Intelligence"
    3. Esperar carga dinámica (JavaScript)
    4. Extraer metadatos de cada resultado
    5. Generar BibTeX entries
    
    **Ventajas:**
    - Maneja contenido dinámico (AJAX)
    - Simula navegador real (evita detección)
    - Screenshots para debugging
    
    **Limitaciones:**
    - Más lento que APIs
    - Sensible a cambios en UI
    
    ---
    
    ### 3️⃣ Unificación de Registros
    
    **Pipeline:**
    
    1. **Carga de fuentes múltiples:**
       - `ieee_combined_*.bib`
       - `semantic_scholar_*.bib`
    
    2. **Parseo BibTeX:**
       ```python
       import bibtexparser
       bib_database = bibtexparser.load(file)
       ```
    
    3. **Deduplicación por DOI:**
       $$
       \\text{unique} = \\{e \\in E : \\text{DOI}(e) \\notin \\text{seen}\\}
       $$
    
    4. **Deduplicación por título (Levenshtein):**
       $$
       \\text{similar}(t_1, t_2) = \\frac{\\text{lev}(t_1, t_2)}{\\max(|t_1|, |t_2|)} < 0.1
       $$
    
    5. **Consolidación:**
       - Merge a `unified_references.bib`
       - Log de duplicados: `removed_duplicates.csv`
    
    ---
    
    ## 📊 Estructura BibTeX
    
    ```bibtex
    @article{key2024,
      title = {Article Title},
      author = {Smith, John and Doe, Jane},
      year = {2024},
      journal = {Journal Name},
      volume = {10},
      pages = {1--20},
      doi = {10.1000/example},
      abstract = {Full abstract text...}
    }
    ```
    
    ---
    
    ## 🔧 Dependencias Técnicas
    
    - **requests:** HTTP requests a Semantic Scholar API
    - **bibtexparser:** Parseo y escritura de BibTeX
    - **playwright:** Web scraping con navegador headless
    - **rapidfuzz:** Similitud de strings (Levenshtein)
    
    ---
    
    ## 💡 Mejores Prácticas
    
    1. **Rate Limiting:** Respetar límites de APIs (Semantic Scholar: ~100 req/min)
    2. **User-Agent:** Identificarse correctamente en requests
    3. **Error Handling:** Logs detallados, continuación tras fallos
    4. **Backups:** Guardar descargas incrementales
    5. **Validation:** Verificar formato BibTeX antes de consolidar
    """)

st.markdown("---")

# Estado del sistema
st.subheader("📊 Estado de Datos")

col1, col2, col3 = st.columns(3)

# Archivos de Semantic Scholar
semantic_dir = PROJECT_ROOT / "data/raw/SemanticScholar"
ieee_dir = PROJECT_ROOT / "data/raw/IEEE"
unified_file = PROJECT_ROOT / "data/processed/unified_references.bib"

with col1:
    if semantic_dir.exists():
        semantic_files = list(semantic_dir.glob("*.bib"))
        st.metric("📄 Archivos Semantic Scholar", len(semantic_files))
        logger.info(f"Archivos Semantic Scholar: {len(semantic_files)}")
    else:
        st.metric("📄 Archivos Semantic Scholar", "0")

with col2:
    if ieee_dir.exists():
        ieee_files = list(ieee_dir.glob("*.bib"))
        st.metric("📄 Archivos IEEE", len(ieee_files))
        logger.info(f"Archivos IEEE: {len(ieee_files)}")
    else:
        st.metric("📄 Archivos IEEE", "0")

with col3:
    if unified_file.exists():
        # Contar entradas en unified
        try:
            import bibtexparser
            with open(unified_file) as f:
                bib_db = bibtexparser.load(f)
                num_entries = len(bib_db.entries)
                st.metric("📚 Referencias Unificadas", num_entries)
                logger.info(f"Referencias unificadas: {num_entries}")
        except:
            st.metric("📚 Referencias Unificadas", "Error")
    else:
        st.metric("📚 Referencias Unificadas", "0")

st.markdown("---")

# Acciones disponibles
st.subheader("🚀 Acciones Disponibles")

tab1, tab2, tab3 = st.tabs(["📥 Semantic Scholar", "🔍 IEEE Xplore", "🔀 Unificar"])

with tab1:
    st.markdown("### Descargar desde Semantic Scholar API")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        query = st.text_input(
            "Query de búsqueda",
            value="Generative Artificial Intelligence",
            help="Términos a buscar en Semantic Scholar"
        )
    
    with col2:
        max_results = st.number_input(
            "Máximo de resultados",
            min_value=10,
            max_value=1000,
            value=100,
            step=10
        )
    
    if st.button("📥 Descargar de Semantic Scholar", type="primary"):
        logger.info(f"Iniciando descarga Semantic Scholar: query='{query}', max={max_results}")
        
        with st.spinner(f"Descargando hasta {max_results} artículos..."):
            try:
                from src.requerimiento1 import scraper
                
                import io
                from contextlib import redirect_stdout
                
                output = io.StringIO()
                with redirect_stdout(output):
                    scraper.download_semantic_scholar(query=query, max_results=max_results)
                
                st.success("✅ Descarga completada")
                logger.info("✅ Descarga Semantic Scholar completada")
                
                with st.expander("📋 Log de descarga"):
                    st.code(output.getvalue())
                
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error: {e}")
                logger.error(f"Error en descarga Semantic Scholar: {e}", exc_info=True)
                st.info("Verifica tu conexión a internet y que Semantic Scholar API esté disponible")

with tab2:
    st.markdown("### Scraper de IEEE Xplore (Playwright)")
    
    st.warning("⚠️ El scraper de IEEE requiere Playwright instalado")
    st.code("playwright install chromium", language="bash")
    
    if st.button("🔍 Ejecutar Scraper IEEE", type="primary"):
        logger.info("Iniciando scraper IEEE Xplore")
        
        st.info("⏳ Este proceso puede tomar varios minutos...")
        
        with st.spinner("Scrapeando IEEE Xplore con Playwright..."):
            try:
                from src.requerimiento1 import ieee_scraper
                
                import io
                from contextlib import redirect_stdout
                
                output = io.StringIO()
                with redirect_stdout(output):
                    ieee_scraper.main()
                
                st.success("✅ Scraping completado")
                logger.info("✅ Scraping IEEE completado")
                
                with st.expander("📋 Log de scraping"):
                    st.code(output.getvalue())
                
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error: {e}")
                logger.error(f"Error en scraping IEEE: {e}", exc_info=True)
                st.info("Asegúrate de tener Playwright instalado: `playwright install chromium`")

with tab3:
    st.markdown("### Unificar y Deduplicar Registros")
    
    st.info("💡 Este paso consolida todos los archivos BibTeX en uno solo, eliminando duplicados")
    
    # Verificar si hay archivos para unificar
    has_files = False
    if semantic_dir.exists() and list(semantic_dir.glob("*.bib")):
        has_files = True
    if ieee_dir.exists() and list(ieee_dir.glob("*.bib")):
        has_files = True
    
    if not has_files:
        st.warning("⚠️ No hay archivos BibTeX para unificar. Descarga primero desde las fuentes.")
    
    if st.button("🔀 Unificar Referencias", type="primary", disabled=not has_files):
        logger.info("Iniciando unificación de referencias")
        
        with st.spinner("Unificando y deduplicando..."):
            try:
                from src.requerimiento1 import unify_records
                
                import io
                from contextlib import redirect_stdout
                
                output = io.StringIO()
                with redirect_stdout(output):
                    unify_records.unify_bib_files()
                
                st.success("✅ Unificación completada")
                logger.info("✅ Unificación de referencias completada")
                
                with st.expander("📋 Log de unificación"):
                    st.code(output.getvalue())
                
                # Mostrar estadísticas
                if unified_file.exists():
                    try:
                        import bibtexparser
                        with open(unified_file) as f:
                            bib_db = bibtexparser.load(f)
                            st.metric("📚 Total de referencias únicas", len(bib_db.entries))
                    except:
                        pass
                
                # Mostrar duplicados removidos
                duplicates_file = PROJECT_ROOT / "data/logs/removed_duplicates.csv"
                if duplicates_file.exists():
                    try:
                        df_dup = pd.read_csv(duplicates_file)
                        st.metric("🗑️ Duplicados removidos", len(df_dup))
                        
                        with st.expander("📋 Ver duplicados removidos"):
                            st.dataframe(df_dup, use_container_width=True)
                    except:
                        pass
                
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error: {e}")
                logger.error(f"Error en unificación: {e}", exc_info=True)

st.markdown("---")

# Archivo unificado
if unified_file.exists():
    st.subheader("📚 Archivo Unificado")
    
    try:
        import bibtexparser
        with open(unified_file) as f:
            bib_db = bibtexparser.load(f)
        
        st.success(f"✅ `unified_references.bib` disponible con **{len(bib_db.entries)} entradas**")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.info("📂 Ubicación: `data/processed/unified_references.bib`")
        
        with col2:
            # Botón de descarga
            with open(unified_file) as f:
                st.download_button(
                    "📥 Descargar",
                    f.read(),
                    "unified_references.bib",
                    "text/plain"
                )
        
        # Mostrar preview
        with st.expander("👁️ Preview (primeras 5 entradas)"):
            for i, entry in enumerate(bib_db.entries[:5]):
                st.markdown(f"**{i+1}. {entry.get('title', 'Sin título')}**")
                st.caption(f"Autores: {entry.get('author', 'Desconocido')} | Año: {entry.get('year', 'N/A')}")
                st.markdown("---")
        
        logger.info(f"Archivo unificado mostrado: {len(bib_db.entries)} entradas")
        
    except Exception as e:
        st.error(f"Error al leer archivo unificado: {e}")
        logger.error(f"Error leyendo unified_references.bib: {e}", exc_info=True)
else:
    st.info("ℹ️ No hay archivo unificado. Descarga y unifica referencias primero.")

st.markdown("---")
st.caption("🔬 [Req1] Automatización de Descarga | Semantic Scholar + IEEE Xplore + Unificación")
