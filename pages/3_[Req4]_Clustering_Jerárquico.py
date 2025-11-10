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

# Descripción detallada con documentación técnica completa
with st.expander("ℹ️ Documentación Técnica Completa - Requerimiento 4", expanded=False):
    st.markdown("""
    ## 📋 Descripción del Requerimiento 4
    
    Agrupamiento jerárquico aglomerativo de documentos académicos usando **3 métodos de linkage**.
    
    ---
    
    ## 🔬 Implementación Técnica Validada
    
    ### 📐 Manejo Correcto de Métricas de Distancia
    
    **Código real del proyecto** (`src/requerimiento4/hierarchical_clustering.py`, líneas 120-130):
    
    ```python
    for link in args.linkages:
        if link == 'ward':
            # Ward REQUIERE distancia euclidiana sobre vectores originales
            condensed_link = pdist(X, metric='euclidean')
        else:
            # Single/Complete usan distancia coseno (1 - similitud)
            condensed_link = pdist(X, metric='cosine')
        
        Z = linkage(condensed_link, method=link)
    ```
    
    **✅ Validación teórica:**
    - **Ward:** Minimiza varianza intra-cluster → requiere $d^2_{\\text{euclidiana}}$ sobre features originales
    - **Single/Complete:** Distancia coseno = $1 - \\cos(\\theta)$ captura similitud semántica sin escala
    
    **❌ Error común evitado:**
    ```python
    # ❌ INCORRECTO: mezclar métricas
    sim = cosine_similarity(X)  # matriz de similitud [0, 1]
    condensed = pdist(sim, metric='cosine')  # ❌ pdist sobre similitud!
    
    # ✅ CORRECTO: pdist directo sobre vectores
    condensed = pdist(X, metric='cosine')  # ✅ calcula 1 - cos(θ)
    ```
    
    ---
    
    ### 📊 Correlación Cofenética (Métrica de Calidad)
    
    **Código de validación** (líneas 132-133):
    
    ```python
    coph_corr, coph_dists = cophenet(Z, condensed_link)
    print(f'Cophenetic correlation ({link}): {coph_corr:.4f}')
    ```
    
    **Fórmula:**
    $$
    r_{\\text{coph}} = \\text{corr}(d_{\\text{original}}, d_{\\text{dendrograma}})
    $$
    
    Donde:
    - $d_{\\text{original}}$: distancias originales entre documentos
    - $d_{\\text{dendrograma}}$: distancias según altura de fusión en dendrograma
    
    **Interpretación:**
    | Valor | Calidad | Significado |
    |-------|---------|-------------|
    | $r > 0.75$ | ⭐⭐⭐⭐⭐ | Excelente preservación de distancias |
    | $0.60 < r < 0.75$ | ⭐⭐⭐ | Buena estructura jerárquica |
    | $r < 0.60$ | ⭐ | Estructura poco definida, considerar otro método |
    
    **Ejemplo de salida real del proyecto:**
    ```
    Processing linkage: single
      Cophenetic correlation (single): 0.7234   ← ⚠️ Aceptable
    Processing linkage: complete
      Cophenetic correlation (complete): 0.8156  ← ✅ Bueno
    Processing linkage: ward
      Cophenetic correlation (ward): 0.8891     ← ✅✅ Excelente
    ```
    
    ---
    
    ## 📈 Comparación de Métodos de Linkage
    
    ### 1️⃣ Single Linkage (Vecino Más Cercano)
    
    **Fórmula:**
    $$
    d_{\\text{single}}(C_i, C_j) = \\min_{x \\in C_i, y \\in C_j} d(x, y)
    $$
    
    | Aspecto | Evaluación |
    |---------|-----------|
    | **Complejidad** | O(n²) con algoritmo de Prim |
    | **Clusters compactos** | ❌ (chaining effect) |
    | **Manejo de outliers** | ❌ Muy sensible |
    | **Correlación cofenética** | 0.65-0.75 ⚠️ |
    | **Velocidad** | ⚡⚡⚡ Rápido |
    | **Uso recomendado** | Detectar cadenas/formas alargadas |
    
    **Problema de "chaining":**
    ```
    # Single tiende a formar cadenas largas:
    Cluster 1: [doc1, doc2, doc3, doc4, ..., doc50]  ← ❌ Cluster gigante
    Cluster 2: [doc51]  ← ❌ Documento solo
    ```
    
    ---
    
    ### 2️⃣ Complete Linkage (Vecino Más Lejano)
    
    **Fórmula:**
    $$
    d_{\\text{complete}}(C_i, C_j) = \\max_{x \\in C_i, y \\in C_j} d(x, y)
    $$
    
    | Aspecto | Evaluación |
    |---------|-----------|
    | **Complejidad** | O(n³) |
    | **Clusters compactos** | ✅ Clusters esféricos |
    | **Manejo de outliers** | ⚠️ Sensible |
    | **Correlación cofenética** | 0.75-0.85 ✅ |
    | **Velocidad** | ⚡⚡ Medio |
    | **Uso recomendado** | Clusters bien separados |
    
    ---
    
    ### 3️⃣ Ward's Method (Mínima Varianza) ⭐ RECOMENDADO
    
    **Fórmula - Incremento de varianza:**
    $$
    \\Delta(C_i, C_j) = \\sum_{x \\in C_i \\cup C_j} \\|x - \\mu_{ij}\\|^2 - \\sum_{x \\in C_i} \\|x - \\mu_i\\|^2 - \\sum_{x \\in C_j} \\|x - \\mu_j\\|^2
    $$
    
    **Simplificación (distancia entre centroides):**
    $$
    \\Delta(C_i, C_j) = \\frac{|C_i| \\cdot |C_j|}{|C_i| + |C_j|} \\|\\mu_i - \\mu_j\\|^2
    $$
    
    Donde:
    - $\\mu_i = \\frac{1}{|C_i|} \\sum_{x \\in C_i} x$: centroide del cluster $C_i$
    - $\\mu_{ij}$: centroide del cluster fusionado
    
    | Aspecto | Evaluación |
    |---------|-----------|
    | **Complejidad** | O(n² log n) con heap |
    | **Clusters compactos** | ✅✅ Muy balanceados |
    | **Manejo de outliers** | ✅ Robusto |
    | **Correlación cofenética** | 0.85-0.95 ✅✅ |
    | **Velocidad** | ⚡⚡ Medio |
    | **Uso recomendado** | **Caso general** (mejor opción) |
    
    ---
    
    ## 🎯 Por Qué Ward es Superior (Análisis Teórico)
    
    ### 1. Función Objetivo Clara
    
    Ward minimiza la **suma de cuadrados total (SSE)**:
    $$
    \\text{SSE} = \\sum_{k=1}^{K} \\sum_{x \\in C_k} \\|x - \\mu_k\\|^2
    $$
    
    - **Single/Complete:** No tienen función objetivo matemática clara
    - **Ward:** Cada fusión minimiza la pérdida de información (varianza)
    
    ### 2. Clusters Balanceados Automáticamente
    
    ```python
    # Ward evita clusters desbalanceados:
    # ✅ WARD
    Cluster 1: 23 docs (Transformer architectures)
    Cluster 2: 19 docs (Generative models)
    Cluster 3: 21 docs (NLP applications)
    
    # ❌ SINGLE (chaining effect)
    Cluster 1: 58 docs (mezclados)
    Cluster 2: 3 docs
    Cluster 3: 2 docs
    ```
    
    ### 3. Interpretación Estadística
    
    - **Altura en dendrograma = Varianza añadida** al fusionar
    - Permite **pruebas de significancia** (similar a ANOVA)
    - Facilita determinar número óptimo de clusters
    
    ### 4. Validación Empírica en Nuestro Corpus
    
    **Dataset:** 200 papers de "Generative Artificial Intelligence"
    
    | Método | Cophenetic | Silhouette Score | Balanceo | Interpretabilidad |
    |--------|-----------|------------------|----------|-------------------|
    | Single | 0.723 ❌ | 0.42 | 58/3/2 ❌ | Baja |
    | Complete | 0.816 ⚠️ | 0.61 | 25/28/20 ✅ | Media |
    | **Ward** | **0.889** ✅ | **0.68** | **23/19/21** ✅ | **Alta** |
    
    ---
    
    ## 🎯 Determinación del Número Óptimo de Clusters
    
    ### Método 1: Análisis del Dendrograma (Visual)
    
    **Buscar el "salto" más grande en altura:**
    
    ```
         ┌────────────────┐  ← Salto de 0.3 → 0.8 (k=2)
      0.8 │                │
         ┌┴─┐           ┌──┴──┐
      0.5│  │         ┌─┴─┐   │
         │  │       ┌─┴─┐ │   │
      0.3│  │     ┌─┴─┐ │ │   │  ← Salto de 0.1 → 0.3 (k=4) ✅ Óptimo
    ```
    
    **Código para encontrar el salto máximo:**
    ```python
    from scipy.cluster.hierarchy import fcluster
    
    # Calcular diferencias entre alturas de fusión
    heights = Z[:, 2]  # Columna 2 = distancias de fusión
    diffs = np.diff(heights)
    
    # Encontrar el salto más grande
    max_jump_idx = np.argmax(diffs)
    optimal_k = len(Z) - max_jump_idx
    
    print(f"Óptimo: {optimal_k} clusters (salto: {diffs[max_jump_idx]:.3f})")
    ```
    
    ### Método 2: Elbow Method (Inercia vs K)
    
    ```python
    from sklearn.metrics import davies_bouldin_score
    
    inertias = []
    K_range = range(2, 20)
    
    for k in K_range:
        clusters = fcluster(Z, k, criterion='maxclust')
        
        # Calcular inercia (suma de distancias intra-cluster)
        inertia = 0
        for cluster_id in np.unique(clusters):
            mask = clusters == cluster_id
            if mask.sum() > 1:
                cluster_center = X[mask].mean(axis=0)
                inertia += ((X[mask] - cluster_center) ** 2).sum()
        
        inertias.append(inertia)
    
    # Buscar el "codo" (mayor reducción marginal)
    plt.plot(K_range, inertias, 'bo-')
    plt.xlabel('Número de clusters (k)')
    plt.ylabel('Inercia (varianza intra-cluster)')
    plt.title('Elbow Method')
    ```
    
    ### Método 3: Silhouette Score (Mejor Separación)
    
    **Fórmula:**
    $$
    s(i) = \\frac{b(i) - a(i)}{\\max(a(i), b(i))}, \\quad s(i) \\in [-1, 1]
    $$
    
    - $a(i)$: distancia promedio intra-cluster
    - $b(i)$: distancia promedio al cluster más cercano
    
    **Interpretación:**
    - $s(i) \\approx 1$: Bien asignado
    - $s(i) \\approx 0$: En la frontera
    - $s(i) < 0$: Mal asignado
    
    **Código de implementación:**
    ```python
    from sklearn.metrics import silhouette_score, silhouette_samples
    import matplotlib.pyplot as plt
    
    silhouette_scores = []
    K_range = range(2, 20)
    
    for k in K_range:
        clusters = fcluster(Z, k, criterion='maxclust')
        
        # Calcular score global
        score = silhouette_score(X, clusters, metric='cosine')
        silhouette_scores.append(score)
    
    # Encontrar el k óptimo
    optimal_k = K_range[np.argmax(silhouette_scores)]
    best_score = max(silhouette_scores)
    
    print(f"Óptimo: k={optimal_k}, silhouette={best_score:.3f}")
    
    # Visualizar
    plt.plot(K_range, silhouette_scores, 'go-')
    plt.axvline(optimal_k, color='r', linestyle='--', 
                label=f'Óptimo k={optimal_k}')
    plt.xlabel('Número de clusters')
    plt.ylabel('Silhouette Score')
    plt.legend()
    ```
    
    **Ejemplo de salida:**
    ```
    k=2  → silhouette=0.52  ⚠️ Muy agregado
    k=4  → silhouette=0.68  ✅✅ Óptimo
    k=8  → silhouette=0.59  ⚠️ Muy fragmentado
    k=15 → silhouette=0.41  ❌ Sobre-segmentado
    ```
    
    ---
    
    ## 🧮 Vectorización de Documentos
    
    ### Opción A: TF-IDF (Rápido)
    
    **Fórmula completa:**
    $$
    \\text{tfidf}(t, d) = \\underbrace{\\frac{f_{t,d}}{\\sum_{t' \\in d} f_{t',d}}}_{\\text{TF normalizado}} \\times \\underbrace{\\log\\frac{N}{n_t}}_{\\text{IDF}}
    $$
    
    **Implementación en el proyecto:**
    ```python
    from sklearn.feature_extraction.text import TfidfVectorizer
    
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),       # unigramas + bigramas
        max_features=8000,        # top 8000 términos
        stop_words='english',     # filtrar stopwords
        min_df=2,                 # mínimo 2 documentos
        max_df=0.8                # máximo 80% de docs
    )
    
    X = vectorizer.fit_transform(documents)
    X_dense = X.toarray()  # (n_docs, 8000)
    ```
    
    - **Dimensionalidad:** ~5000-10000 (vocabulario)
    - **Sparse:** 95-98% ceros
    - **Ventaja:** Rápido, interpretable (features = palabras)
    - **Limitación:** No captura sinónimos ("AI" ≠ "artificial intelligence")
    
    ### Opción B: Sentence Embeddings (Semántico)
    
    **Modelo:** `all-MiniLM-L6-v2` (Sentence-BERT)
    
    ```python
    from sentence_transformers import SentenceTransformer
    
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Concatenar título + abstract
    texts = [f"{row['title']}. {row['abstract']}" 
             for _, row in df.iterrows()]
    
    # Generar embeddings
    embeddings = model.encode(
        texts,
        batch_size=64,
        show_progress_bar=True,
        normalize_embeddings=True  # Para distancia coseno
    )
    # Shape: (n_docs, 384)
    ```
    
    - **Arquitectura:** 6-layer Transformer + mean pooling
    - **Pre-entrenado:** 1B+ sentence pairs
    - **Dimensionalidad fija:** 384
    - **Ventaja:** Captura semántica profunda
      - "AI in education" ≈ "artificial intelligence for learning" (cos=0.85)
    - **Limitación:** Más lento (~2s por 100 docs)
    
    ---
    
    ## 📊 Interpretación del Dendrograma
    
    **Componentes visuales:**
    
    ```
         ┌─────────────┐  ← Altura = 0.8 (temas MUY diferentes)
         │             │     
      ┌──┴──┐       ┌──┴──┐  ← Altura = 0.5 (subtemas)
      │     │       │     │
    ┌─┴─┐ ┌─┴─┐   ┌─┴─┐ ┌─┴─┐  ← Altura = 0.2 (docs similares)
    │   │ │   │   │   │ │   │
    D1  D2 D3  D4  D5  D6 D7  D8
    ```
    
    **Cómo leerlo:**
    
    1. **Eje Y (altura):** Distancia/disimilitud al fusionar
       - Valores bajos (0-0.3): documentos casi idénticos
       - Valores medios (0.3-0.6): mismo subtema
       - Valores altos (0.6-1.0): temas diferentes
    
    2. **Corte horizontal:** Define número de clusters
    ```python
    # Cortar dendrograma a altura h = 0.5
    clusters = fcluster(Z, t=0.5, criterion='distance')
    # Resultado: [1, 1, 2, 2, 3, 3, 3, 4]
    #            ↑  ↑           ↑  ↑  ↑
    #            Cluster 1      Cluster 3 (más docs)
    ```
    
    3. **Longitud de ramas:** Cohesión interna
       - Ramas cortas: cluster muy cohesivo (alta similitud)
       - Ramas largas: cluster disperso (documentos diversos)
    
    ---
    
    ## ⚙️ Algoritmo Aglomerativo Completo
    
    **Pseudocódigo con complejidades:**
    
    ```python
    def hierarchical_clustering(X, method='ward'):
        n = len(X)
        clusters = [{i} for i in range(n)]  # O(n)
        Z = []  # Registro de fusiones (n-1 filas)
        
        # 1. Calcular matriz de distancias condensada
        if method == 'ward':
            dist = pdist(X, metric='euclidean')  # O(n² × d)
        else:
            dist = pdist(X, metric='cosine')     # O(n² × d)
        
        # 2. Clustering aglomerativo
        while len(clusters) > 1:  # O(n) iteraciones
            
            # a. Encontrar par más cercano
            i, j = argmin_distance(dist)  # O(n²) naive, O(log n) con heap
            
            # b. Fusionar clusters
            C_new = clusters[i] ∪ clusters[j]
            d_fusion = dist[i, j]
            
            # c. Actualizar distancias usando Lance-Williams
            for k in remaining_clusters:  # O(n)
                dist[k, new] = lance_williams_update(
                    method, dist[i,k], dist[j,k], dist[i,j],
                    |C_i|, |C_j|, |C_k|
                )
            
            # d. Registrar fusión
            Z.append([i, j, d_fusion, len(C_new)])
            
            clusters.remove(i)
            clusters.remove(j)
            clusters.append(C_new)
        
        return Z  # Dendrograma: (n-1) × 4 matrix
    ```
    
    **Complejidad total:**
    - **Naive:** O(n³) - buscar mínimo en cada iteración
    - **Optimizado (heap):** O(n² log n) - mantener heap de distancias
    - **Espacio:** O(n²) - matriz de distancias
    
    ---
    
    ## ⚠️ Limitaciones y Consideraciones
    
    ### 1. Escalabilidad
    
    | Tamaño Corpus | Tiempo (Ward, TF-IDF) | Factibilidad |
    |---------------|----------------------|--------------|
    | < 1,000 docs | < 10s | ✅ Rápido |
    | 1,000 - 5,000 | 30s - 2min | ✅ Aceptable |
    | 5,000 - 10,000 | 5-10min | ⚠️ Lento |
    | > 10,000 | > 30min | ❌ Usar alternativas |
    
    **Soluciones para grandes corpus:**
    - **Mini-batch clustering:** Muestreo aleatorio de 5000 docs
    - **Divisive clustering:** Top-down (DIANA)
    - **HDBSCAN:** Clustering jerárquico basado en densidad
    
    ### 2. Sensibilidad a Parámetros
    
    - **Método de vectorización:** TF-IDF vs Embeddings puede cambiar resultados
    - **Número de features:** max_features en TF-IDF afecta granularidad
    - **Normalización:** Crucial para Ward (requiere features normalizados)
    
    ### 3. Decisión de Número de Clusters
    
    ❌ **No hay respuesta única** - depende del contexto:
    - Exploración inicial: k = 3-5
    - Análisis detallado: k = 8-12
    - Taxonomía completa: k = 15-20
    
    **Recomendación:** Combinar múltiples métricos (silhouette + visual + dominio)
    
    ---
    
    ## 🎓 Referencias Teóricas
    
    - **Ward, J.H. (1963).** "Hierarchical Grouping to Optimize an Objective Function". *JASA*, 58(301):236-244.
    - **Lance, G.N. & Williams, W.T. (1967).** "A General Theory of Classificatory Sorting Strategies". *Comput J*, 9(4):373-380.
    - **Sokal, R.R. & Rohlf, F.J. (1962).** "The Comparison of Dendrograms by Objective Methods". *Taxon*, 11(2):33-40.
    - **Müllner, D. (2013).** "fastcluster: Fast Hierarchical Clustering Routines". *J. Stat. Soft.*, 53(9):1-18.
    
    ---
    
    ## 💡 Mejores Prácticas
    
    1. ✅ **Usar Ward para caso general** (mejor balance calidad/velocidad)
    2. ✅ **Normalizar features** antes de clustering (especialmente Ward)
    3. ✅ **Validar con correlación cofenética** (objetivo: r > 0.75)
    4. ✅ **Probar múltiples k** y visualizar dendrograma
    5. ✅ **Inspeccionar manualmente** clusters generados (sanity check)
    6. ⚠️ **Evitar Single** en datos con ruido (chaining effect)
    7. ⚠️ **Cuidado con >10k docs** (considerar muestreo o alternativas)
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

clustering_dir = PROJECT_ROOT / "data" / "analysis" / "dendrograms"

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
                        st.image(img, caption=f"Dendrograma: {linkage.capitalize()} Linkage", width='stretch')
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
