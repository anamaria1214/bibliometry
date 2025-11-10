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

# Descripción detallada con documentación técnica completa
with st.expander("ℹ️ Documentación Técnica Completa - Requerimiento 3", expanded=False):
    st.markdown("""
    ## 📋 Descripción del Requerimiento 3
    
    Este módulo realiza **análisis de frecuencia de términos** en la literatura académica usando dos enfoques complementarios.
    
    ---
    
    ## 🔬 Implementación Técnica Validada
    
    ### 1️⃣ Conteo Directo de Términos (Pattern Matching)
    
    Identifica palabras clave predefinidas usando **búsqueda con expresiones regulares**.
    
    **Fórmula de frecuencia:**
    $$
    \\text{freq}(t) = \\sum_{d \\in D} \\sum_{i=1}^{|d|} \\mathbb{1}_{\\text{match}(t, d_i)}
    $$
    
    Donde:
    - $t$: término de interés (puede ser multiword)
    - $D$: corpus de documentos (abstracts)
    - $\\mathbb{1}_{\\text{match}(t, d_i)}$: 1 si el patrón $t$ aparece en posición $i$ de documento $d$
    
    **Implementación real** (`src/requerimiento3/analyze_bib_category.py`, líneas 112-145):
    
    ```python
    def count_seed_terms_in_abstracts(abstracts, seed_terms_norm):
        \"\"\"
        Cuenta ocurrencias totales y número de abstracts que contienen cada término.
        Usa word boundaries (\\b) para evitar falsos positivos.
        \"\"\"
        total_occ = Counter()      # Total de ocurrencias en todo el corpus
        abstracts_occ = Counter()  # Número de abstracts con el término
        
        for item in abstracts:
            abs_text = normalize_text(item["abstract"])
            
            for term_raw, term_norm in zip(SEED_TERMS, seed_terms_norm):
                if not term_norm:
                    continue
                
                # Búsqueda con word boundaries para multi-word terms
                # \\b asegura match de palabras completas
                pattern = r'\\b' + re.escape(term_norm) + r'\\b'
                occurrences = len(re.findall(pattern, abs_text))
                
                # Fallback: si no hay match exacto, buscar tokens individuales
                if occurrences == 0:
                    term_tokens = term_norm.split()
                    token_occ = sum(
                        1 for tok in term_tokens 
                        if re.search(r'\\b' + re.escape(tok) + r'\\b', abs_text)
                    )
                    if token_occ > 0:
                        occurrences = token_occ  # Conteo aproximado
                
                if occurrences > 0:
                    total_occ[term_raw] += occurrences
                    abstracts_occ[term_raw] += 1  # Abstract count (0 o 1 por doc)
        
        return total_occ, abstracts_occ
    ```
    
    **✅ Validación con ejemplos:**
    
    ```python
    # Ejemplo 1: Match exacto
    text = "large language models are transforming NLP"
    term = "large language models"
    # → occurrences = 1 ✅
    
    # Ejemplo 2: Match parcial (fallback)
    text = "language model capabilities"
    term = "large language models"  # Falta "large" y plural
    # → Búsqueda exacta: 0
    # → Búsqueda tokens: ["large"→0, "language"→1, "models"→0]
    # → occurrences = 1 (fallback) ⚠️
    
    # Ejemplo 3: Word boundaries previenen falsos positivos
    text = "enlargement of models"
    term = "large"
    # → occurrences = 0 ✅ (NO match "enlarge")
    ```
    
    | Aspecto | Valor |
    |---------|-------|
    | **Complejidad** | O(n × m × k) donde n=docs, m=términos, k=longitud promedio |
    | **Precision** | Alta (word boundaries + normalización) |
    | **Recall** | Media (no captura sinónimos ni variantes) |
    | **Ventaja** | Rápido, reproducible, interpretable |
    | **Limitación** | Requiere términos predefinidos, inflexible |
    
    **Términos predefinidos del proyecto:**
    ```python
    SEED_TERMS = [
        "Generative models",     "Prompting",
        "Machine learning",      "Multimodality",
        "Fine-tuning",           "Training data",
        "Algorithmic bias",      "Explainability",
        "Transparency",          "Ethics",
        "Privacy",               "Personalization",
        "Human-AI interaction",  "AI literacy",
        "Co-creation"
    ]
    ```
    
    ---
    
    ### 2️⃣ Descubrimiento Algorítmico con TF-IDF
    
    Identifica automáticamente términos relevantes sin supervisión.
    
    **Fórmula TF-IDF completa:**
    $$
    \\text{tfidf}(t, d, D) = \\underbrace{\\frac{f_{t,d}}{\\sum_{t' \\in d} f_{t',d}}}_{\\text{TF normalizado}} \\times \\underbrace{\\log\\frac{|D|}{|\\{d' \\in D : t \\in d'\\}|}}_{\\text{IDF}}
    $$
    
    **Suma agregada para ranking:**
    $$
    \\text{TF-IDF}_{\\text{total}}(t) = \\sum_{d \\in D} \\text{tfidf}(t, d, D)
    $$
    
    **Implementación real** (líneas 148-201):
    
    ```python
    from sklearn.feature_extraction.text import TfidfVectorizer
    
    def discover_terms_with_tfidf(
        abstract_texts, 
        seed_terms_norm, 
        top_n=15, 
        ngram_range=(1,2),  # Unigramas + bigramas
        max_features=5000
    ):
        \"\"\"
        Vectoriza corpus con TF-IDF y selecciona top términos
        excluyendo palabras semilla (para evitar redundancia).
        \"\"\"
        # Normalizar textos
        docs = [normalize_text(t) for t in abstract_texts]
        
        # Vectorizar con TF-IDF
        vectorizer = TfidfVectorizer(
            ngram_range=ngram_range,  # (1,2) = unigramas + bigramas
            max_features=max_features,
            stop_words='english',      # Filtrar "the", "is", etc.
            token_pattern=r'(?u)\\b\\w+\\b',
            min_df=2                   # Mínimo 2 documentos
        )
        
        X = vectorizer.fit_transform(docs)  # Matriz sparse (n_docs × vocab_size)
        feature_names = np.array(vectorizer.get_feature_names_out())
        
        # Suma de TF-IDF por término (across all docs)
        tfidf_sum = np.asarray(X.sum(axis=0)).ravel()
        
        # Document frequency (#docs con el término)
        doc_freq = np.asarray((X > 0).sum(axis=0)).ravel()
        
        # Filtrar seed terms (evitar descubrir términos ya conocidos)
        seed_set = set(seed_terms_norm)
        candidates = []
        
        for i, fname in enumerate(feature_names):
            if fname in seed_set:
                continue  # Saltar términos semilla
            
            # Filtrar tokens muy cortos o numéricos
            if len(fname) < 2 or fname.isdigit():
                continue
            
            candidates.append((fname, tfidf_sum[i], doc_freq[i], i))
        
        # Ordenar por TF-IDF total (descendente)
        candidates_sorted = sorted(candidates, key=lambda x: x[1], reverse=True)
        
        # Seleccionar top_n
        selected = []
        for fname, s, df, idx_col in candidates_sorted[:top_n*5]:
            # Filtrar términos que son substrings de seed terms
            normalized = fname
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
        
        return selected, vectorizer, X
    ```
    
    **✅ Validación paso a paso:**
    
    ```python
    # Corpus de ejemplo (3 abstracts)
    docs = [
        "generative adversarial networks for image synthesis",
        "transformers and attention mechanisms in NLP",
        "diffusion models for text-to-image generation"
    ]
    
    # Paso 1: Vectorización TF-IDF
    # Vocabulario: ["adversarial", "attention", "diffusion", "gan", "generative", ...]
    # Matriz X: (3 docs × 50 terms)
    
    # Paso 2: TF-IDF scores (ejemplo)
    #   "diffusion" → TF-IDF_sum = 0.68 (aparece en 1 doc, alta especificidad)
    #   "generation" → TF-IDF_sum = 0.61 (aparece en 1 doc)
    #   "networks" → TF-IDF_sum = 0.45 (común)
    #   "the" → TF-IDF_sum = 0.00 (stopword, filtrado)
    
    # Paso 3: Ranking
    # Top 3: ["diffusion", "generation", "adversarial"] ✅
    ```
    
    | Aspecto | Valor |
    |---------|-------|
    | **Complejidad** | O(n × d) donde d = max_features |
    | **Unsupervised** | ✅ No requiere términos predefinidos |
    | **Descubre emergentes** | ✅ Identifica términos nuevos |
    | **Ventaja** | Adaptativo, captura tendencias |
    | **Limitación** | Sensible a ruido, no semántico |
    
    ---
    
    ### 📊 Validación de Calidad: Similitud con Seed Terms
    
    Calcula qué tan relacionado está cada término descubierto con los términos semilla.
    
    **Similitud coseno en espacio TF-IDF:**
    $$
    \\text{sim}(t_{\\text{auto}}, t_{\\text{seed}}) = \\frac{\\mathbf{v}_{\\text{auto}} \\cdot \\mathbf{v}_{\\text{seed}}}{\\|\\mathbf{v}_{\\text{auto}}\\| \\|\\mathbf{v}_{\\text{seed}}\\|}
    $$
    
    **Implementación** (líneas 215-267):
    
    ```python
    def compute_similarity_to_seeds(
        selected_terms,  # Términos descubiertos
        vectorizer,      # TF-IDF vectorizer fitted
        X,               # Matriz TF-IDF del corpus
        seed_terms_norm,
        abstract_texts
    ):
        \"\"\"
        Calcula similitud de cada término descubierto con todos los seed terms.
        Retorna max_similarity para validar relevancia.
        \"\"\"
        seed_set = set(seed_terms_norm)
        
        for term_data in selected_terms:
            term_norm = normalize_text(term_data["term"])
            
            # Vector TF-IDF del término descubierto
            col_idx = term_data["col_index"]
            term_vector = X[:, col_idx].toarray().ravel()  # (n_docs,)
            
            # Calcular similitud con cada seed term
            similarities = []
            for seed in seed_terms_norm:
                if seed in vectorizer.vocabulary_:
                    seed_idx = vectorizer.vocabulary_[seed]
                    seed_vector = X[:, seed_idx].toarray().ravel()
                    
                    # Cosine similarity
                    dot_product = np.dot(term_vector, seed_vector)
                    norm_product = np.linalg.norm(term_vector) * np.linalg.norm(seed_vector)
                    
                    sim = dot_product / norm_product if norm_product > 0 else 0.0
                    similarities.append(sim)
            
            # Guardar max_similarity
            term_data["max_similarity_to_seed"] = max(similarities) if similarities else 0.0
        
        return selected_terms
    ```
    
    **Interpretación de similitud:**
    
    | Similitud | Interpretación | Acción |
    |-----------|----------------|--------|
    | > 0.50 | Fuertemente relacionado | ✅ Altamente relevante |
    | 0.30-0.50 | Moderadamente relacionado | ⚠️ Revisar manualmente |
    | < 0.30 | Débilmente relacionado | ❌ Posible ruido |
    
    **Ejemplo de salida real:**
    ```
    Auto-discovered terms:
    1. "neural networks"     → max_sim=0.72 (seed: "machine learning") ✅
    2. "prompt engineering"  → max_sim=0.65 (seed: "prompting") ✅
    3. "algorithmic fairness"→ max_sim=0.58 (seed: "algorithmic bias") ✅
    4. "computer vision"     → max_sim=0.41 (seed: "multimodality") ⚠️
    5. "dataset"             → max_sim=0.28 (seed: "training data") ❌
    
    Precision @ 0.30: 4/5 = 80%  ← Métrica de calidad
    ```
    
    ---
    
    ## 🎯 Metodología Completa del Pipeline
    
    ### Paso 1: Preprocesamiento de Texto
    
    **Función de normalización** (líneas 56-62):
    
    ```python
    from unidecode import unidecode
    
    def normalize_text(s: str) -> str:
        \"\"\"Normaliza texto para búsqueda y comparación\"\"\"
        s = s or ""
        s = unidecode(s)                  # Quitar tildes: "José" → "Jose"
        s = s.lower()                     # Lowercase
        s = re.sub(r"[^a-z0-9\\s\\-]", " ", s)  # Solo alfanumérico + espacios
        s = re.sub(r"\\s+", " ", s).strip()     # Colapsar espacios múltiples
        return s
    ```
    
    **Ejemplo:**
    ```python
    normalize_text("Large Language Models (LLMs)!")
    # → "large language models llms"
    ```
    
    ### Paso 2: Extracción de Abstracts desde BibTeX
    
    **Parsing regex** (líneas 73-108):
    
    ```python
    def read_bib_file_extract_abstracts(bib_path: Path):
        \"\"\"
        Lee .bib y extrae abstracts con parsing robusto.
        Retorna: [{'key': str, 'title': str, 'abstract': str}, ...]
        \"\"\"
        text = bib_path.read_text(encoding="utf-8", errors="ignore")
        
        # Separar entradas: @TYPE{...}
        raw_entries = re.findall(
            r'@[\\w]+\\s*{[^@]*}', 
            text, 
            flags=re.DOTALL | re.IGNORECASE
        )
        
        results = []
        for idx, entry in enumerate(raw_entries, start=1):
            # Extraer key
            mkey = re.match(r'@[\\w]+\\s*{\\s*([^,]+),', entry)
            key = mkey.group(1).strip() if mkey else f"entry_{idx}"
            
            # Extraer title (opcional)
            mtitle = re.search(r'title\\s*=\\s*[{"](.*?)[}"]', entry, re.IGNORECASE)
            title = mtitle.group(1).strip() if mtitle else ""
            
            # Extraer abstract (soporta múltiples formatos)
            mabs1 = re.search(r'abstract\\s*=\\s*{(.+?)}(?=,\\s*\\w+\\s*=|\\s*})', 
                             entry, re.IGNORECASE | re.DOTALL)
            mabs2 = re.search(r'abstract\\s*=\\s*"(.+?)"', entry, re.IGNORECASE | re.DOTALL)
            
            abstract = ""
            if mabs1:
                abstract = mabs1.group(1).strip().replace("\\n", " ")
            elif mabs2:
                abstract = mabs2.group(1).strip().replace("\\n", " ")
            
            results.append({
                "key": key,
                "title": title,
                "abstract": abstract
            })
        
        return results
    ```
    
    ### Paso 3: Cálculo de Métricas
    
    **Outputs generados:**
    
    1. **`category_frequencies.csv`:**
    ```csv
    category,seed_term,total_occurrences,num_abstracts_with_term
    Generative AI,Generative models,45,32
    Generative AI,Prompting,28,21
    Generative AI,Machine learning,67,48
    ...
    ```
    
    2. **`auto_discovered_terms.csv`:**
    ```csv
    term,tfidf_sum,doc_freq,max_similarity_to_seed
    neural networks,12.45,38,0.72
    prompt engineering,9.87,25,0.65
    algorithmic fairness,8.23,19,0.58
    ...
    ```
    
    3. **`precision_report.txt`:**
    ```
    Category: Concepts of Generative AI in Education
    Seed terms (count): 15
    
    --- Seed frequency summary ---
    [tabla con conteos]
    
    --- Auto-discovered terms ---
    [términos + similitudes]
    
    --- Precision summary ---
    Similarity threshold: 0.30
    Auto-discovered terms total: 15
    Terms with similarity >= threshold: 12
    Precision: 0.800  ← 80% de términos relevantes
    ```
    
    ---
    
    ## 📊 Interpretación de Resultados
    
    ### Conteo Directo: Análisis de Presencia
    
    | Frecuencia | Interpretación | Implicación |
    |------------|----------------|-------------|
    | > 50 ocurrencias | **Tema central** | Área madura con mucha investigación |
    | 20-50 | **Tema importante** | Suficiente literatura para revisión |
    | 5-20 | **Tema emergente** | Área en crecimiento |
    | 1-5 | **Nicho** | Mención esporádica |
    | 0 | **Gap de investigación** | Oportunidad para nuevo trabajo |
    
    **Ejemplo de análisis:**
    ```
    "Machine learning": 67 ocurrencias en 48/200 abstracts (24%)
    → Tema fundamental, presente en 1 de cada 4 papers ✅
    
    "AI literacy": 3 ocurrencias en 3/200 abstracts (1.5%)
    → Tema emergente, poca cobertura actual ⚠️
    ```
    
    ### TF-IDF: Análisis de Distintividad
    
    **Alto TF-IDF significa:**
    - ✅ Término **distintivo** del corpus (no genérico)
    - ✅ Aparece en documentos específicos (alto IDF)
    - ✅ Con frecuencia significativa en esos docs (alto TF)
    
    **Bajo TF-IDF significa:**
    - ❌ Término muy común (bajo IDF)
    - ❌ O aparece pocas veces (bajo TF)
    
    **Ejemplo:**
    ```
    "prompt engineering" → TF-IDF_sum = 9.87
    - Aparece en 25/200 docs (IDF moderado-alto)
    - Con frecuencia alta en esos docs (TF alto)
    → Término distintivo del corpus sobre Gen AI ✅
    
    "system" → TF-IDF_sum = 2.14
    - Aparece en 150/200 docs (IDF muy bajo)
    - Término genérico, poco informativo ❌
    ```
    
    ---
    
    ## 🔧 Parámetros Configurables (en código fuente)
    
    ```python
    # src/requerimiento3/analyze_bib_category.py
    
    # TF-IDF discovery parameters
    top_n = 15              # Top N términos a descubrir
    ngram_range = (1, 2)    # (1,1)=solo palabras, (1,2)=palabras+bigramas
    max_features = 5000     # Vocabulario máximo (más = más lento)
    min_df = 2              # Mínimo docs para incluir término
    
    # Similarity threshold
    similarity_threshold = 0.30  # Umbral para considerar término relevante
    ```
    
    **Impacto de parámetros:**
    
    | Parámetro | ↑ Aumentar | ↓ Disminuir |
    |-----------|-----------|-------------|
    | `top_n` | Más términos descubiertos | Menos términos (más selectivo) |
    | `ngram_range[1]` | Captura frases (bigramas/trigramas) | Solo palabras individuales |
    | `max_features` | Mayor vocabulario (más lento) | Vocabulario reducido (más rápido) |
    | `min_df` | Solo términos muy comunes | Incluye términos raros |
    | `similarity_threshold` | Solo términos muy similares a seeds | Incluye términos más diversos |
    
    ---
    
    ## 💡 Aplicaciones Prácticas
    
    ### 1. Revisión Sistemática de Literatura
    
    **Uso:**
    - Identificar subtemas principales
    - Cuantificar cobertura de cada tema
    - Detectar gaps (términos con frecuencia = 0)
    
    **Ejemplo:**
    ```
    Corpus: 200 papers de "Generative AI in Education"
    
    Hallazgos:
    - "Prompting" (28 occ) << "Machine learning" (67 occ)
      → Prompting está subrepresentado en educación
    - "AI literacy" (3 occ) → Gap de investigación identificado
      → Oportunidad para nuevo trabajo
    ```
    
    ### 2. Trend Analysis (Análisis Temporal)
    
    **Uso:**
    - Comparar frecuencias entre períodos
    - Identificar términos emergentes (crecimiento rápido)
    
    **Ejemplo:**
    ```
    2020: "Diffusion models" = 2 ocurrencias
    2023: "Diffusion models" = 43 ocurrencias
    → Crecimiento 21× en 3 años ✅ Término emergente
    ```
    
    ### 3. Keyword Extraction para Taxonomías
    
    **Uso:**
    - Construir vocabulario controlado
    - Generar tags automáticamente
    - Crear jerarquías de conceptos
    
    **Ejemplo:**
    ```
    Top términos TF-IDF:
    1. "neural networks" → Categoría: Architectures
    2. "prompt engineering" → Categoría: Techniques
    3. "algorithmic bias" → Categoría: Ethics
    → Taxonomía emergente del corpus
    ```
    
    ---
    
    ## 📈 Comparación: Conteo Directo vs TF-IDF
    
    | Aspecto | Conteo Directo | TF-IDF Discovery |
    |---------|---------------|------------------|
    | **Supervisión** | ✅ Totalmente supervisado (términos predefinidos) | ❌ Unsupervised |
    | **Reproducibilidad** | ✅✅ 100% | ⚠️ Depende de corpus |
    | **Descubre nuevos términos** | ❌ No | ✅✅ Sí |
    | **Interpretabilidad** | ✅✅ Clara (conteo simple) | ⚠️ Requiere interpretar TF-IDF |
    | **Robustez a ruido** | ✅ Alta (word boundaries) | ⚠️ Media (sensible a términos genéricos) |
    | **Velocidad** | ⚡⚡⚡ Muy rápido | ⚡⚡ Medio (vectorización) |
    | **Mejor para** | Validar hipótesis predefinidas | Exploración abierta |
    
    **Recomendación:** Usar **ambos enfoques** de forma complementaria:
    1. Conteo directo → Confirmar términos conocidos
    2. TF-IDF → Descubrir términos emergentes
    3. Validación cruzada → Similitud entre descubiertos y conocidos
    
    ---
    
    ## 🎓 Referencias Teóricas
    
    - **Salton & Buckley (1988):** "Term-weighting approaches in automatic text retrieval"
    - **Sparck Jones (1972):** "A statistical interpretation of term specificity and its application in retrieval"
    - **Manning, Raghavan & Schütze (2008):** "Introduction to Information Retrieval" (Cap. 6: Scoring, term weighting)
    
    ---
    
    ## ⚠️ Limitaciones y Consideraciones
    
    ### Conteo Directo
    
    1. **No captura variantes:**
       - "fine-tuning" ≠ "fine tuning" ≠ "finetuning"
       - Solución: Agregar variantes a seed terms
    
    2. **No captura sinónimos:**
       - "machine learning" ≠ "ML"
       - Solución: Incluir abreviaciones
    
    3. **Sensible a cambios de vocabulario:**
       - Términos emergentes no se detectan
       - Solución: Actualizar seed terms periódicamente
    
    ### TF-IDF Discovery
    
    1. **Ruido de términos genéricos:**
       - "system", "approach", "method" tienen alto TF-IDF pero poca información
       - Solución: Filtrado manual o blacklist
    
    2. **No semántico:**
       - "neural network" ≠ "neural net" (tratados como distintos)
       - Solución: Usar embeddings (Word2Vec/SBERT) en lugar de TF-IDF
    
    3. **Dependiente del corpus:**
       - Resultados cambian con corpus diferente
       - Solución: Validación con similitud a seed terms
    
    ---
    
    ## 🚀 Extensiones Futuras
    
    1. **Análisis temporal:**
       - Frecuencias por año → Detectar trends
       - Clustering temporal de términos
    
    2. **Co-ocurrencia de términos:**
       - Matriz de co-ocurrencia → Relaciones entre términos
       - Network analysis de conceptos
    
    3. **Embeddings semánticos:**
       - Reemplazar TF-IDF por SBERT
       - Clustering de términos semánticamente similares
    
    4. **Topic Modeling:**
       - LDA / BERTopic para temas latentes
       - Interpretación automática de clusters
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
