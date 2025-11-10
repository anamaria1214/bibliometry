.PHONY: help install menu clean test
.DEFAULT_GOAL := help

# Colores para output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

##@ General

help: ## Muestra este mensaje de ayuda
	@echo "$(BLUE)═══════════════════════════════════════════════════════════════════$(NC)"
	@echo "$(GREEN)  Sistema de Análisis Bibliométrico - Makefile$(NC)"
	@echo "$(BLUE)═══════════════════════════════════════════════════════════════════$(NC)"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf "Uso: make $(YELLOW)<target>$(NC)\n\n"} \
		/^[a-zA-Z_0-9-]+:.*?##/ { printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2 } \
		/^##@/ { printf "\n$(BLUE)%s$(NC)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)
	@echo ""

install: ## Instala todas las dependencias desde requirements.txt
	@echo "$(GREEN)📦 Instalando dependencias...$(NC)"
	pip install -r requirements.txt
	@echo "$(GREEN)✅ Dependencias instaladas correctamente$(NC)"
	@echo "$(YELLOW)⚠️  Recuerda: Para usar IEEE scraper ejecuta 'make install-browsers'$(NC)"

install-browsers: ## Instala los navegadores de Playwright (requerido para IEEE scraper)
	@echo "$(YELLOW)🌐 Instalando navegadores de Playwright...$(NC)"
	@echo "$(BLUE)ℹ️  Descargando Chromium (~100MB)...$(NC)"
	playwright install chromium
	@echo "$(GREEN)✅ Navegadores instalados correctamente$(NC)"

install-all: install install-browsers ## Instala dependencias + navegadores de Playwright

menu: ## Ejecuta el menú interactivo principal
	@echo "$(GREEN)🚀 Iniciando menú principal...$(NC)"
	python menu.py

clean: ## Elimina archivos temporales y cache de Python
	@echo "$(YELLOW)🧹 Limpiando archivos temporales...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".DS_Store" -delete
	@echo "$(GREEN)✅ Limpieza completada$(NC)"

##@ Requerimiento 1: Automatización de Descarga

req1-semantic: ## Descarga artículos desde Semantic Scholar API
	@echo "$(GREEN)🔄 Descargando desde Semantic Scholar...$(NC)"
	@echo "$(YELLOW)📝 Búsqueda: 'Generative Artificial Intelligence'$(NC)"
	python src/requerimiento1/scraper.py

req1-ieee: ## Scraping de artículos desde IEEE Xplore (requiere Playwright)
	@echo "$(GREEN)🔄 Iniciando scraper de IEEE...$(NC)"
	@echo "$(YELLOW)⚠️  Requiere: playwright install$(NC)"
	python src/requerimiento1/ieee_scraper.py

req1-unify: ## Unifica y deduplica registros .bib de data/raw/
	@echo "$(GREEN)🔄 Unificando registros bibliográficos...$(NC)"
	@echo "$(YELLOW)📂 Input: data/raw/IEEE/ y data/raw/SemanticScholar/$(NC)"
	@echo "$(YELLOW)📂 Output: data/processed/unified_references.bib$(NC)"
	python src/requerimiento1/unify_records.py

req1-all: req1-semantic req1-ieee req1-unify ## Ejecuta todo el flujo de descarga y unificación

##@ Requerimiento 2: Similitud Textual

req2-app: ## Inicia aplicación Streamlit de similitud textual (6 algoritmos)
	@echo "$(GREEN)🚀 Iniciando aplicación de similitud...$(NC)"
	@echo "$(BLUE)📊 Algoritmos:$(NC)"
	@echo "   • Levenshtein (edición)"
	@echo "   • Jaccard (conjuntos)"
	@echo "   • Coseno TF-IDF (vectorización)"
	@echo "   • Euclidiana (vectores)"
	@echo "   • Sentence-BERT (embeddings)"
	@echo "   • Word2Vec (embeddings)"
	@echo ""
	@echo "$(YELLOW)🌐 Se abrirá en http://localhost:8501$(NC)"
	streamlit run src/requerimiento2/similitud_textual_app.py

req2-app-custom: ## Inicia app con archivo .bib personalizado
	@echo "$(GREEN)🚀 Iniciando aplicación de similitud...$(NC)"
	@read -p "Ruta del archivo .bib: " bibfile; \
	streamlit run src/requerimiento2/similitud_textual_app.py -- --bib-file "$$bibfile"

##@ Requerimiento 3: Análisis de Frecuencia

req3-analyze: ## Analiza frecuencia de términos (conteo directo + TF-IDF)
	@echo "$(GREEN)📊 Analizando frecuencia de términos...$(NC)"
	@echo "$(YELLOW)📂 Input: data/processed/unified_references.bib$(NC)"
	@echo "$(YELLOW)📂 Output: data/analysis/$(NC)"
	@echo "   • category_frequencies.csv"
	@echo "   • auto_discovered_terms.csv"
	@echo "   • precision_report.txt"
	python src/requerimiento3/analyze_bib_category.py

##@ Requerimiento 4: Agrupamiento Jerárquico

req4-tfidf: ## Clustering jerárquico con TF-IDF (hasta 200 documentos)
	@echo "$(GREEN)🌳 Clustering jerárquico con TF-IDF...$(NC)"
	@echo "$(YELLOW)⚙️  Parámetros:$(NC)"
	@echo "   • Método: TF-IDF vectorization"
	@echo "   • Max docs: 200"
	@echo "   • Linkages: single, complete, ward"
	python src/requerimiento4/hierarchical_clustering.py --method tfidf --max-docs 200

req4-embeddings: ## Clustering con Sentence-BERT embeddings (hasta 100 documentos)
	@echo "$(GREEN)🌳 Clustering con embeddings semánticos...$(NC)"
	@echo "$(YELLOW)⚙️  Parámetros:$(NC)"
	@echo "   • Método: Sentence-BERT (all-MiniLM-L6-v2)"
	@echo "   • Max docs: 100"
	@echo "   • Linkages: single, complete, ward"
	python src/requerimiento4/hierarchical_clustering.py --method embeddings --max-docs 100

req4-tfidf-custom: ## Clustering TF-IDF con parámetros personalizados
	@echo "$(GREEN)🌳 Clustering jerárquico personalizado...$(NC)"
	@read -p "Número máximo de documentos [200]: " maxdocs; \
	maxdocs=$${maxdocs:-200}; \
	python src/requerimiento4/hierarchical_clustering.py --method tfidf --max-docs $$maxdocs

req4-embeddings-custom: ## Clustering embeddings con parámetros personalizados
	@echo "$(GREEN)🌳 Clustering con embeddings personalizado...$(NC)"
	@read -p "Número máximo de documentos [100]: " maxdocs; \
	maxdocs=$${maxdocs:-100}; \
	python src/requerimiento4/hierarchical_clustering.py --method embeddings --max-docs $$maxdocs

req4-all: req4-tfidf req4-embeddings ## Ejecuta ambos métodos de clustering

##@ Requerimiento 5: Visualizaciones

req5-visualize: ## Genera todas las visualizaciones (heatmap, wordcloud, timeline)
	@echo "$(GREEN)📈 Generando visualizaciones...$(NC)"
	@echo "$(BLUE)📊 Visualizaciones:$(NC)"
	@echo "   • Mapa de calor geográfico"
	@echo "   • Nube de palabras"
	@echo "   • Línea temporal de publicaciones"
	python src/requerimiento5/cli_visualize.py

req5-extract-metadata: ## Extrae metadata de .bib a CSV
	@echo "$(GREEN)📋 Extrayendo metadata...$(NC)"
	@echo "$(YELLOW)📂 Input: data/processed/unified_references.bib$(NC)"
	@echo "$(YELLOW)📂 Output: data/analysis/metadata.csv$(NC)"
	python src/requerimiento5/extract_metadata.py

req5-extract-custom: ## Extrae metadata con archivo personalizado
	@echo "$(GREEN)📋 Extrayendo metadata...$(NC)"
	@read -p "Archivo .bib de entrada: " bibfile; \
	read -p "Archivo CSV de salida: " csvfile; \
	python src/requerimiento5/extract_metadata.py --bib-file "$$bibfile" --output "$$csvfile"

##@ Flujos Completos

workflow-download: req1-all ## Flujo completo de descarga (Semantic + IEEE + Unificar)
	@echo "$(GREEN)✅ Descarga y unificación completada$(NC)"

workflow-analysis: req3-analyze req4-all req5-visualize ## Flujo completo de análisis
	@echo "$(GREEN)✅ Análisis completo finalizado$(NC)"

workflow-full: workflow-download workflow-analysis ## Flujo completo: descarga + análisis
	@echo "$(GREEN)✅ Pipeline completo ejecutado$(NC)"

##@ Desarrollo y Testing

test-imports: ## Verifica que todos los imports funcionen correctamente
	@echo "$(YELLOW)🧪 Verificando imports...$(NC)"
	@python -c "from src.requerimiento1 import scraper; print('✅ requerimiento1.scraper')"
	@python -c "from src.requerimiento1 import unify_records; print('✅ requerimiento1.unify_records')"
	@python -c "from src.requerimiento3 import analyze_bib_category; print('✅ requerimiento3.analyze_bib_category')"
	@python -c "from src.requerimiento5 import extract_metadata; print('✅ requerimiento5.extract_metadata')"
	@echo "$(GREEN)✅ Todos los imports son válidos$(NC)"

check-data: ## Verifica la estructura de directorios data/
	@echo "$(YELLOW)🔍 Verificando estructura de datos...$(NC)"
	@test -d data/raw && echo "$(GREEN)✅ data/raw/$(NC)" || echo "$(RED)❌ data/raw/ no existe$(NC)"
	@test -d data/processed && echo "$(GREEN)✅ data/processed/$(NC)" || echo "$(RED)❌ data/processed/ no existe$(NC)"
	@test -d data/analysis && echo "$(GREEN)✅ data/analysis/$(NC)" || echo "$(RED)❌ data/analysis/ no existe$(NC)"
	@test -d data/logs && echo "$(GREEN)✅ data/logs/$(NC)" || echo "$(RED)❌ data/logs/ no existe$(NC)"

check-deps: ## Verifica que las dependencias principales estén instaladas
	@echo "$(YELLOW)🔍 Verificando dependencias...$(NC)"
	@python -c "import pandas" 2>/dev/null && echo "$(GREEN)✅ pandas$(NC)" || echo "$(RED)❌ pandas$(NC)"
	@python -c "import sklearn" 2>/dev/null && echo "$(GREEN)✅ scikit-learn$(NC)" || echo "$(RED)❌ scikit-learn$(NC)"
	@python -c "import scipy" 2>/dev/null && echo "$(GREEN)✅ scipy$(NC)" || echo "$(RED)❌ scipy$(NC)"
	@python -c "import sentence_transformers" 2>/dev/null && echo "$(GREEN)✅ sentence-transformers$(NC)" || echo "$(RED)❌ sentence-transformers$(NC)"
	@python -c "import streamlit" 2>/dev/null && echo "$(GREEN)✅ streamlit$(NC)" || echo "$(RED)❌ streamlit$(NC)"
	@python -c "import playwright" 2>/dev/null && echo "$(GREEN)✅ playwright$(NC)" || echo "$(RED)❌ playwright$(NC)"

info: ## Muestra información detallada de argumentos por módulo
	@echo "$(BLUE)═══════════════════════════════════════════════════════════════════$(NC)"
	@echo "$(GREEN)  INFORMACIÓN DETALLADA DE ARGUMENTOS$(NC)"
	@echo "$(BLUE)═══════════════════════════════════════════════════════════════════$(NC)"
	@echo ""
	@echo "$(YELLOW)📦 REQUERIMIENTO 1: Automatización de Descarga$(NC)"
	@echo "────────────────────────────────────────────────────────────────────"
	@echo "$(GREEN)scraper.py$(NC) (Semantic Scholar)"
	@echo "  • Sin argumentos (hardcoded: 'Generative Artificial Intelligence')"
	@echo "  • Output: data/raw/SemanticScholar/*.bib"
	@echo ""
	@echo "$(GREEN)ieee_scraper.py$(NC) (IEEE Xplore)"
	@echo "  • Sin argumentos CLI (configuración interna)"
	@echo "  • Requiere: playwright install"
	@echo "  • Output: data/raw/IEEE/*.bib"
	@echo ""
	@echo "$(GREEN)unify_records.py$(NC)"
	@echo "  • Sin argumentos"
	@echo "  • Input: data/raw/IEEE/ + data/raw/SemanticScholar/"
	@echo "  • Output: data/processed/unified_references.bib"
	@echo ""
	@echo "$(YELLOW)📊 REQUERIMIENTO 2: Similitud Textual$(NC)"
	@echo "────────────────────────────────────────────────────────────────────"
	@echo "$(GREEN)similitud_textual_app.py$(NC) (Streamlit)"
	@echo "  --bib-file PATH       Ruta al archivo .bib"
	@echo "                        Default: data/processed/unified_references.bib"
	@echo "  • Algoritmos: Levenshtein, Jaccard, Coseno, Euclidiana,"
	@echo "                Sentence-BERT, Word2Vec"
	@echo ""
	@echo "$(YELLOW)📈 REQUERIMIENTO 3: Análisis de Frecuencia$(NC)"
	@echo "────────────────────────────────────────────────────────────────────"
	@echo "$(GREEN)analyze_bib_category.py$(NC)"
	@echo "  • Sin argumentos"
	@echo "  • Input: data/processed/unified_references.bib"
	@echo "  • Output: data/analysis/category_frequencies.csv"
	@echo "           data/analysis/auto_discovered_terms.csv"
	@echo "           data/analysis/precision_report.txt"
	@echo ""
	@echo "$(YELLOW)🌳 REQUERIMIENTO 4: Clustering Jerárquico$(NC)"
	@echo "────────────────────────────────────────────────────────────────────"
	@echo "$(GREEN)hierarchical_clustering.py$(NC)"
	@echo "  --method METHOD       Método de vectorización:"
	@echo "                        • tfidf (TF-IDF)"
	@echo "                        • embeddings (Sentence-BERT)"
	@echo "                        Default: tfidf"
	@echo ""
	@echo "  --max-docs N          Número máximo de documentos"
	@echo "                        Default: 200 (tfidf), 100 (embeddings)"
	@echo ""
	@echo "  --bib-file PATH       Ruta al archivo .bib"
	@echo "                        Default: data/processed/unified_references.bib"
	@echo ""
	@echo "  --output-dir PATH     Directorio de salida"
	@echo "                        Default: data/analysis/"
	@echo ""
	@echo "  • Linkages generados: single, complete, ward"
	@echo "  • Salida: dendrogramas PNG + métricas cophenet"
	@echo ""
	@echo "$(YELLOW)📊 REQUERIMIENTO 5: Visualizaciones$(NC)"
	@echo "────────────────────────────────────────────────────────────────────"
	@echo "$(GREEN)extract_metadata.py$(NC)"
	@echo "  --bib-file PATH       Archivo .bib de entrada"
	@echo "                        Default: data/processed/unified_references.bib"
	@echo ""
	@echo "  --output PATH         Archivo CSV de salida"
	@echo "                        Default: data/analysis/metadata.csv"
	@echo ""
	@echo "$(GREEN)cli_visualize.py$(NC)"
	@echo "  • Menú interactivo sin argumentos"
	@echo "  • Genera: heatmap geográfico, wordcloud, timeline"
	@echo "  • Input: data/analysis/metadata.csv"
	@echo "  • Output: data/analysis/*.png + combined.pdf"
	@echo ""
	@echo "$(BLUE)═══════════════════════════════════════════════════════════════════$(NC)"

##@ Ejecutar Streamlit

run: ## Ejecuta la aplicación Streamlit (app.py)
	@echo "$(GREEN)🚀 Iniciando Streamlit App...$(NC)"
	@echo "$(BLUE)📡 Abriendo http://localhost:8501$(NC)"
	streamlit run app.py

##@ Limpieza de Datos

clean-logs: ## Elimina logs temporales
	@echo "$(YELLOW)🧹 Limpiando logs...$(NC)"
	rm -f data/logs/*.csv
	@echo "$(GREEN)✅ Logs eliminados$(NC)"

clean-analysis: ## Elimina resultados de análisis
	@echo "$(YELLOW)🧹 Limpiando análisis...$(NC)"
	@read -p "¿Estás seguro? Esto eliminará data/analysis/* [y/N]: " confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		rm -f data/analysis/*.csv data/analysis/*.png data/analysis/*.pdf data/analysis/*.txt; \
		echo "$(GREEN)✅ Análisis eliminado$(NC)"; \
	else \
		echo "$(YELLOW)❌ Cancelado$(NC)"; \
	fi

clean-all: clean clean-logs ## Limpia cache de Python y logs
	@echo "$(GREEN)✅ Limpieza completa finalizada$(NC)"
