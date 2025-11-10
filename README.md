# 📚 Bibliometry - Sistema de Análisis Bibliométrico

Sistema modular para análisis de publicaciones académicas sobre **Inteligencia Artificial Generativa**, con interfaz web integrada y herramientas avanzadas de análisis.

## 🚀 Características Principales

### 🔍 **Requerimiento 1**: Automatización de Descarga
- Scrapers para IEEE Xplore y Semantic Scholar API
- Unificación automática de registros BibTeX
- Deduplicación inteligente por DOI/título

### 📊 **Requerimiento 2**: Similitud Textual (6 Algoritmos)
- Levenshtein Distance
- Jaccard Similarity
- Coseno TF-IDF
- Euclidiana
- Sentence-BERT (Transformers)
- Word2Vec

### 📈 **Requerimiento 3**: Análisis de Frecuencia
- Conteo directo de términos
- Descubrimiento algorítmico con TF-IDF
- Exportación a CSV y gráficos

### 🌳 **Requerimiento 4**: Clustering Jerárquico
- Métodos: Single, Complete, Ward
- Vectorización: TF-IDF y Sentence Embeddings
- Dendrogramas interactivos

### 🗺️ **Requerimiento 5**: Visualizaciones
- Mapa de calor geográfico de publicaciones
- Nube de palabras de términos clave
- Línea temporal de evolución

### 🖥️ **Requerimiento 6**: Dashboard Streamlit
- Interfaz web unificada con navegación multi-página
- Visualización integrada de todos los módulos
- Sistema de estado y monitoreo

### 🤖 **Requerimiento 7**: Sistema de Recomendación Híbrido
- **70%** Similitud Semántica (Sentence-BERT)
- **30%** Similitud de Keywords (Jaccard)
- Recomendaciones configurables por score

---

## 📦 Instalación

### Opción 1: Instalación Local

#### Requisitos Previos
- Python 3.10+ (probado con 3.13)
- pip
- Git

#### Pasos

```bash
# Clonar repositorio
git clone <url-del-repo>
cd bibliometry

# Crear entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Instalar dependencias
pip install -r requirements.txt \
    --extra-index-url https://download.pytorch.org/whl/cpu \
    -c constraints.txt

# Instalar navegadores de Playwright
playwright install chromium
```

#### Usando Make (Linux/Mac)

```bash
# Instalación completa (Python + Playwright)
make install-all

# Solo Python
make install

# Solo Playwright
make install-browsers
```

### Opción 2: Docker 🐳

```bash
# Construir imagen
docker build -t bibliometry .

# Ejecutar contenedor
docker run -p 8501:8501 bibliometry

# Acceder al dashboard
# http://localhost:8501
```

### Opción 3: Deploy en la Nube ☁️

Para deploy completo con **Playwright + IEEE scraper funcional**, consulta [`DEPLOY.md`](./DEPLOY.md).

**Opciones recomendadas:**

| Plataforma | Precio/mes | RAM | Setup | Recomendado |
|------------|-----------|-----|-------|-------------|
| **Railway** | ~$5* | 8GB | 🟢 Fácil | ⭐⭐⭐⭐⭐ |
| **DigitalOcean** | $12 | 1GB | 🟢 Fácil | ⭐⭐⭐⭐ |
| **Fly.io** | $5-8 | 2GB | 🟢 Fácil | ⭐⭐⭐⭐ |
| **VPS (Hetzner)** | €4.5 | 4GB | 🔴 Manual | ⭐⭐⭐⭐⭐ |

*Railway incluye $5 crédito gratis mensual

**Quick Start (Railway):**
1. Ve a [railway.app](https://railway.app)
2. Deploy from GitHub → conecta este repo
3. Railway detecta Dockerfile automáticamente
4. Deploy → ¡Listo en 5 minutos!

Ver guía completa en [`DEPLOY.md`](./DEPLOY.md) con instrucciones paso a paso para cada plataforma.

---

## 🎯 Uso

### Dashboard Web (Recomendado)

```bash
# Ejecutar dashboard Streamlit
streamlit run app.py

# O usando el menú
python menu.py
# Seleccionar opción 6
```

El dashboard estará disponible en **http://localhost:8501**

### Menú CLI

```bash
python menu.py
```

Navega por las opciones 1-7 para acceder a cada módulo.

### Uso Individual de Módulos

#### Requerimiento 1: Descargar Referencias

```bash
# Semantic Scholar API
python src/requerimiento1/scraper.py

# Unificar archivos .bib
python src/requerimiento1/unify_records.py
```

#### Requerimiento 2: Similitud Textual

```bash
streamlit run src/requerimiento2/similitud_textual_app.py
```

#### Requerimiento 3: Análisis de Frecuencia

```bash
python src/requerimiento3/analyze_bib_category.py
```

#### Requerimiento 4: Clustering

```bash
# TF-IDF
python src/requerimiento4/hierarchical_clustering.py \
    --method tfidf --max-docs 200

# Embeddings
python src/requerimiento4/hierarchical_clustering.py \
    --method embeddings --max-docs 100
```

#### Requerimiento 5: Visualizaciones

```bash
python src/requerimiento5/cli_visualize.py
```

#### Requerimiento 7: Sistema de Recomendación

```bash
python src/requerimiento7/recommender.py \
    --article-index 0 \
    --num-recommendations 5
```

---

## 📂 Estructura del Proyecto

```
bibliometry/
├── app.py                          # Dashboard principal
├── menu.py                         # Menú CLI
├── Dockerfile                      # Containerización
├── requirements.txt                # Dependencias
├── Makefile                        # Automatización
│
├── pages/                          # Páginas Streamlit
│   ├── 1_📊_Similitud_Textual.py
│   ├── 2_📈_Análisis_de_Frecuencia.py
│   ├── 3_🌳_Clustering_Jerárquico.py
│   ├── 4_🗺️_Visualizaciones.py
│   └── 5_🤖_Sistema_de_Recomendación.py
│
├── src/
│   ├── requerimiento1/             # Descarga
│   ├── requerimiento2/             # Similitud
│   ├── requerimiento3/             # Frecuencia
│   ├── requerimiento4/             # Clustering
│   ├── requerimiento5/             # Visualizaciones
│   └── requerimiento7/             # Recomendador
│
└── data/
    ├── raw/                        # BibTeX originales
    ├── processed/                  # unified_references.bib
    ├── analysis/                   # CSVs, gráficos
    └── logs/
```

---

## 🛠️ Stack Tecnológico

- **Python 3.13** + **PyTorch 2.9.0** (CPU)
- **Streamlit 1.51.0** (Dashboard)
- **Sentence-Transformers 5.1.2** (NLP)
- **scikit-learn 1.7.2** (ML)
- **matplotlib/seaborn/plotly** (Viz)
- **Playwright 1.55.0** (Scraping)

---

## 🐛 Troubleshooting

### `ModuleNotFoundError: bibtexparser`
```bash
pip install bibtexparser==1.4.3
```

### `Playwright executable doesn't exist`
```bash
playwright install chromium
```

### `FileNotFoundError: unified_references.bib`
```bash
# Ejecuta primero Requerimiento 1
python src/requerimiento1/scraper.py
python src/requerimiento1/unify_records.py
```

### Error 429 (Rate Limit)
El scraper tiene retry automático. Si persiste, espera unos minutos.

---

## 📝 Notas de Desarrollo

### Sistema de Recomendación (Req. 7)

**Score Híbrido:**
```
score = 0.7 × similitud_semántica + 0.3 × similitud_keywords
```

- **Semántica**: all-MiniLM-L6-v2, 384d embeddings, cosine similarity
- **Keywords**: Top 20 términos, Jaccard index

### Clustering (Req. 4)

- **Complejidad**: O(n³) para Single/Complete/Ward
- **Ward**: Minimiza varianza intra-cluster
