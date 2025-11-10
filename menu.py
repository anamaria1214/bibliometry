#!/usr/bin/env python3
"""
Menú principal del sistema de análisis bibliométrico
Sistema modular para análisis de publicaciones sobre IA Generativa
"""

import sys
import os
from pathlib import Path

# Añadir src al path para imports
sys.path.insert(0, str(Path(__file__).parent / "src"))


def print_header():
    """Imprime el encabezado del menú"""
    print("\n" + "=" * 70)
    print(" " * 15 + "SISTEMA DE ANÁLISIS BIBLIOMÉTRICO")
    print(" " * 10 + "Generative Artificial Intelligence Research")
    print("=" * 70)


def print_menu():
    """Imprime el menú principal"""
    print("\n    REQUERIMIENTOS FUNCIONALES:\n")
    print("  1.  Automatización de descarga y unificación")
    print("      → Scrapers (IEEE, Semantic Scholar, etc.)")
    print("      → Unificación y deduplicación de registros")
    print()
    print("  2.  Similitud textual (6 algoritmos)")
    print("      → Levenshtein, Jaccard, Coseno TF-IDF")
    print("      → Euclidiana, Sentence-BERT, Word2Vec")
    print()
    print("  3.  Análisis de frecuencia de términos")
    print("      → Conteo directo y generación algorítmica (TF-IDF)")
    print()
    print("  4.  Agrupamiento jerárquico")
    print("      → Clustering: Single, Complete, Ward")
    print()
    print("  5.  Visualizaciones")
    print("      → Mapa de calor, nube de palabras, línea temporal")
    print()
    print("  6.  Dashboard Streamlit")
    print("      → Interfaz web unificada con navegación")
    print()
    print("  7.  Sistema de recomendación híbrido")
    print("      → Sentence-BERT 70% + Jaccard 30%")
    print()
    print("-" * 70)
    print("  0.  Salir")
    print("=" * 70)


def run_requerimiento1():
    """Ejecuta el módulo de automatización de descarga"""
    print("\n" + "=" * 70)
    print("REQUERIMIENTO 1: Automatización de descarga")
    print("=" * 70)
    print("\nOpciones disponibles:")
    print("  1. Descargar desde Semantic Scholar")
    print("  2. Descargar desde IEEE (scraper)")
    print("  3. Unificar registros .bib")
    print("  0. Volver al menú principal")
    
    choice = input("\nSeleccione una opción: ").strip()
    
    if choice == "1":
        from src.requerimiento1 import scraper
        print("\n[info] Iniciando descarga desde Semantic Scholar...")
        scraper.download_semantic_scholar()
    elif choice == "2":
        from src.requerimiento1 import ieee_scraper
        print("\n[info] Iniciando descarga desde IEEE...")
        print("[info]  Por favor ejecute: python src/requerimiento1/ieee_scraper.py")
    elif choice == "3":
        from src.requerimiento1 import unify_records
        print("\n[info] Unificando registros .bib...")
        unify_records.unify_bib_files()
    elif choice == "0":
        return
    else:
        print("[error] Opción no válida")


def run_requerimiento2():
    """Ejecuta el módulo de similitud textual"""
    print("\n" + "=" * 70)
    print("REQUERIMIENTO 2: Similitud textual")
    print("=" * 70)
    print("\n[info] Iniciando aplicación Streamlit de similitud...")
    print("[info] Se abrirá en tu navegador automáticamente")
    
    try:
        os.chdir(Path(__file__).parent)
        os.system("streamlit run src/requerimiento2/similitud_textual_app.py")
    except Exception as e:
        print(f"[error] Error: {e}")
        print("[info]  Por favor ejecute manualmente: streamlit run src/requerimiento2/similitud_textual_app.py")
    
    input("\nPresione Enter para continuar...")


def run_requerimiento3():
    """Ejecuta el análisis de frecuencia"""
    print("\n" + "=" * 70)
    print("REQUERIMIENTO 3: Análisis de frecuencia de términos")
    print("=" * 70)
    print("\n[info] Analizando frecuencia de términos...")
    
    try:
        from src.requerimiento3 import run_analysis
        run_analysis()
    except Exception as e:
        print(f"[error] Error: {e}")
        print("[info]  Por favor ejecute: python src/requerimiento3/analyze_bib_category.py")
    
    input("\nPresione Enter para continuar...")


def run_requerimiento4():
    """Ejecuta el agrupamiento jerárquico"""
    print("\n" + "=" * 70)
    print("REQUERIMIENTO 4: Agrupamiento jerárquico")
    print("=" * 70)
    print("\nOpciones de clustering:")
    print("  1. TF-IDF vectorization")
    print("  2. Sentence embeddings")
    print("  0. Volver")
    
    choice = input("\nSeleccione método de vectorización: ").strip()
    
    if choice == "1":
        print("\n🔄 Ejecutando clustering con TF-IDF...")
        try:
            from src.requerimiento4 import run_clustering
            run_clustering(['--method', 'tfidf', '--max-docs', '200'])
        except Exception as e:
            print(f"[error] Error: {e}")
    elif choice == "2":
        print("\n🔄 Ejecutando clustering con embeddings...")
        try:
            from src.requerimiento4 import run_clustering
            run_clustering(['--method', 'embeddings', '--max-docs', '100'])
        except Exception as e:
            print(f"[error] Error: {e}")
    elif choice == "0":
        return
    else:
        print("[error] Opción no válida")
    
    input("\nPresione Enter para continuar...")


def run_requerimiento5():
    """Ejecuta las visualizaciones"""
    print("\n" + "=" * 70)
    print("REQUERIMIENTO 5: Visualizaciones")
    print("=" * 70)
    print("\nGenerando visualizaciones...")
    print("  • Mapa de calor geográfico")
    print("  • Nube de palabras")
    print("  • Línea temporal de publicaciones")
    
    try:
        from src.requerimiento5 import run_visualizations
        run_visualizations()
    except Exception as e:
        print(f"[error] Error: {e}")
        print("[info]  Por favor ejecute: python src/requerimiento5/cli_visualize.py")
    
    input("\nPresione Enter para continuar...")


def run_requerimiento6():
    """Ejecuta el dashboard Streamlit"""
    print("\n" + "=" * 70)
    print("REQUERIMIENTO 6: Dashboard Streamlit")
    print("=" * 70)
    print("\n[info] Iniciando dashboard de Streamlit...")
    print("[info] Se abrirá en tu navegador automáticamente en http://localhost:8501")
    print("\n[tip] Para detener el servidor presiona Ctrl+C")
    
    try:
        os.chdir(Path(__file__).parent)
        os.system("streamlit run app.py")
    except Exception as e:
        print(f"[error] Error: {e}")
        print("[info]  Por favor ejecute manualmente: streamlit run app.py")
    
    input("\nPresione Enter para continuar...")


def run_requerimiento7():
    """Ejecuta el sistema de recomendación"""
    print("\n" + "=" * 70)
    print("REQUERIMIENTO 7: Sistema de Recomendación Híbrido")
    print("=" * 70)
    print("\n[info] Sistema que combina:")
    print("  • 70% Similitud Semántica (Sentence-BERT)")
    print("  • 30% Similitud de Keywords (Jaccard)")
    
    print("\nOpciones:")
    print("  1. Obtener recomendaciones (modo CLI)")
    print("  2. Abrir interfaz web (Streamlit)")
    print("  0. Volver")
    
    choice = input("\nSeleccione una opción: ").strip()
    
    if choice == "1":
        try:
            article_index = input("\nÍndice del artículo base [0]: ").strip()
            article_index = int(article_index) if article_index else 0
            
            num_recs = input("Número de recomendaciones [5]: ").strip()
            num_recs = int(num_recs) if num_recs else 5
            
            print(f"\n[info] Generando {num_recs} recomendaciones para artículo #{article_index}...")
            
            from src.requerimiento7 import main as rec_main
            rec_main(['--article-index', str(article_index), 
                     '--num-recommendations', str(num_recs)])
            
        except Exception as e:
            print(f"[error] Error: {e}")
            print("[info]  Asegúrate de haber ejecutado primero Visualizaciones para generar metadata.csv")
    
    elif choice == "2":
        print("\n[info] Abriendo interfaz web...")
        try:
            os.chdir(Path(__file__).parent)
            os.system("streamlit run app.py")
        except Exception as e:
            print(f"[error] Error: {e}")
    
    elif choice == "0":
        return
    else:
        print("[error] Opción no válida")
    
    input("\nPresione Enter para continuar...")


def main():
    """Función principal del menú"""
    while True:
        print_header()
        print_menu()
        
        choice = input("\nSeleccione una opción [0-7]: ").strip()
        
        if choice == "1":
            run_requerimiento1()
        elif choice == "2":
            run_requerimiento2()
        elif choice == "3":
            run_requerimiento3()
        elif choice == "4":
            run_requerimiento4()
        elif choice == "5":
            run_requerimiento5()
        elif choice == "6":
            run_requerimiento6()
        elif choice == "7":
            run_requerimiento7()
        elif choice == "0":
            print("\n¡Hasta pronto!")
            print("=" * 70 + "\n")
            sys.exit(0)
        else:
            print("\n[error] Opción no válida. Por favor, seleccione un número del 0 al 7.")
            input("Presione Enter para continuar...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[info] Programa interrumpido por el usuario. ¡Hasta pronto!")
        sys.exit(0)
