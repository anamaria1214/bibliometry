"""
Requerimiento 7: Sistema de Recomendación Híbrido

Combina similitud semántica (Sentence-BERT) con similitud de keywords (Jaccard)
para recomendar artículos académicos relacionados.

Arquitectura:
- 70% peso por defecto para similitud semántica (embeddings)
- 30% peso por defecto para similitud de keywords (Jaccard)
- Configurable vía parámetros

Uso:
    from src.requerimiento7 import get_recommendations
    
    recommendations = get_recommendations(
        article_index=0,
        num_recommendations=5,
        semantic_weight=0.7,
        keyword_weight=0.3
    )
"""

import pandas as pd
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Tuple
import re
from collections import Counter

# Configuración de paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
METADATA_FILE = PROJECT_ROOT / "data/analysis/metadata.csv"

# Modelo de embeddings (lazy loading)
_model = None


def get_model():
    """Carga el modelo Sentence-BERT de forma lazy"""
    global _model
    if _model is None:
        print("Cargando modelo Sentence-BERT (all-MiniLM-L6-v2)...")
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model


def preprocess_text(text: str) -> str:
    """
    Limpia y normaliza texto para procesamiento.
    
    Args:
        text: Texto a limpiar
    
    Returns:
        Texto limpio en minúsculas sin caracteres especiales
    """
    if not isinstance(text, str):
        return ""
    
    # Convertir a minúsculas
    text = text.lower()
    
    # Eliminar caracteres especiales pero conservar espacios
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    
    # Eliminar espacios múltiples
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()


def extract_keywords(text: str, top_n: int = 20) -> set:
    """
    Extrae keywords del texto basándose en frecuencia.
    
    Args:
        text: Texto del cual extraer keywords
        top_n: Número máximo de keywords a retornar
    
    Returns:
        Set de keywords más frecuentes
    """
    # Stopwords comunes en inglés
    stopwords = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
        'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
        'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this',
        'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
        'what', 'which', 'who', 'when', 'where', 'why', 'how', 'all', 'each',
        'every', 'both', 'few', 'more', 'most', 'other', 'some', 'such', 'no',
        'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's',
        't', 'can', 'will', 'just', 'don', 'should', 'now'
    }
    
    # Preprocesar y tokenizar
    clean_text = preprocess_text(text)
    words = clean_text.split()
    
    # Filtrar stopwords y palabras muy cortas
    keywords = [w for w in words if w not in stopwords and len(w) > 2]
    
    # Contar frecuencias y obtener las más comunes
    counter = Counter(keywords)
    top_keywords = {word for word, _ in counter.most_common(top_n)}
    
    return top_keywords


def jaccard_similarity(set1: set, set2: set) -> float:
    """
    Calcula similitud de Jaccard entre dos conjuntos.
    
    Args:
        set1: Primer conjunto
        set2: Segundo conjunto
    
    Returns:
        Índice de Jaccard [0, 1]
    """
    if not set1 or not set2:
        return 0.0
    
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    
    return intersection / union if union > 0 else 0.0


def load_metadata() -> pd.DataFrame:
    """
    Carga archivo de metadata.
    
    Returns:
        DataFrame con metadata de artículos
    
    Raises:
        FileNotFoundError: Si no existe metadata.csv
    """
    if not METADATA_FILE.exists():
        raise FileNotFoundError(
            f"No se encontró {METADATA_FILE}. "
            "Ejecuta primero el módulo de Visualizaciones para extraer metadata."
        )
    
    df = pd.read_csv(METADATA_FILE)
    
    # Rellenar NaN con strings vacíos
    df['title'] = df['title'].fillna('')
    df['abstract'] = df['abstract'].fillna('')
    df['author'] = df['author'].fillna('Desconocido')
    df['year'] = df['year'].fillna(0)
    
    return df


def compute_semantic_similarities(
    base_text: str,
    texts: List[str],
    model: SentenceTransformer
) -> np.ndarray:
    """
    Calcula similitudes semánticas usando Sentence-BERT.
    
    Args:
        base_text: Texto de referencia
        texts: Lista de textos a comparar
        model: Modelo Sentence-BERT
    
    Returns:
        Array de similitudes coseno [0, 1]
    """
    # Generar embeddings
    base_embedding = model.encode([base_text], convert_to_tensor=True)
    embeddings = model.encode(texts, convert_to_tensor=True)
    
    # Calcular similitud coseno
    from sentence_transformers.util import cos_sim
    similarities = cos_sim(base_embedding, embeddings)[0]
    
    return similarities.cpu().numpy()


def compute_keyword_similarities(
    base_keywords: set,
    keywords_list: List[set]
) -> List[float]:
    """
    Calcula similitudes de keywords usando Jaccard.
    
    Args:
        base_keywords: Keywords del artículo base
        keywords_list: Lista de sets de keywords a comparar
    
    Returns:
        Lista de índices de Jaccard
    """
    similarities = []
    
    for keywords in keywords_list:
        sim = jaccard_similarity(base_keywords, keywords)
        similarities.append(sim)
    
    return similarities


def get_recommendations(
    article_index: int,
    num_recommendations: int = 5,
    semantic_weight: float = 0.7,
    keyword_weight: float = 0.3
) -> List[Dict]:
    """
    Obtiene recomendaciones híbridas para un artículo.
    
    Args:
        article_index: Índice del artículo base en metadata.csv
        num_recommendations: Número de recomendaciones a retornar
        semantic_weight: Peso de similitud semántica [0, 1]
        keyword_weight: Peso de similitud de keywords [0, 1]
    
    Returns:
        Lista de diccionarios con recomendaciones ordenadas por score
    
    Raises:
        ValueError: Si los pesos no suman 1 o el índice es inválido
    """
    # Validar pesos
    if not np.isclose(semantic_weight + keyword_weight, 1.0):
        raise ValueError("Los pesos deben sumar 1.0")
    
    # Cargar metadata
    df = load_metadata()
    
    # Validar índice
    if article_index < 0 or article_index >= len(df):
        raise ValueError(f"Índice inválido: {article_index}. Rango válido: [0, {len(df)-1}]")
    
    # Obtener artículo base
    base_article = df.iloc[article_index]
    base_text = f"{base_article['title']} {base_article['abstract']}"
    base_keywords = extract_keywords(base_text)
    
    print(f"Artículo base: {base_article['title'][:60]}...")
    print(f"Keywords extraídas: {len(base_keywords)}")
    
    # Preparar textos de todos los artículos (excepto el base)
    texts = []
    keywords_list = []
    indices = []
    
    for idx, row in df.iterrows():
        if idx == article_index:
            continue
        
        text = f"{row['title']} {row['abstract']}"
        keywords = extract_keywords(text)
        
        texts.append(text)
        keywords_list.append(keywords)
        indices.append(idx)
    
    # Calcular similitud semántica
    print("Calculando similitudes semánticas con Sentence-BERT...")
    model = get_model()
    semantic_sims = compute_semantic_similarities(base_text, texts, model)
    
    # Calcular similitud de keywords
    print("Calculando similitudes de keywords con Jaccard...")
    keyword_sims = compute_keyword_similarities(base_keywords, keywords_list)
    
    # Combinar scores
    hybrid_scores = (
        semantic_weight * semantic_sims +
        keyword_weight * np.array(keyword_sims)
    )
    
    # Crear lista de resultados
    results = []
    for i, idx in enumerate(indices):
        results.append({
            'index': idx,
            'title': df.iloc[idx]['title'],
            'author': df.iloc[idx]['author'],
            'year': int(df.iloc[idx]['year']) if df.iloc[idx]['year'] > 0 else 'N/A',
            'abstract': df.iloc[idx]['abstract'],
            'hybrid_score': float(hybrid_scores[i]),
            'semantic_score': float(semantic_sims[i]),
            'keyword_score': float(keyword_sims[i])
        })
    
    # Ordenar por score híbrido descendente
    results.sort(key=lambda x: x['hybrid_score'], reverse=True)
    
    # Retornar top N
    top_results = results[:num_recommendations]
    
    print(f"✅ Se encontraron {len(top_results)} recomendaciones")
    
    return top_results


def main(argv=None):
    """
    Función principal para uso desde CLI o menu.py
    
    Args:
        argv: Lista de argumentos (opcional)
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Sistema de Recomendación Híbrido (Sentence-BERT + Jaccard)"
    )
    parser.add_argument(
        '--article-index',
        type=int,
        default=0,
        help='Índice del artículo base (default: 0)'
    )
    parser.add_argument(
        '--num-recommendations',
        type=int,
        default=5,
        help='Número de recomendaciones (default: 5)'
    )
    parser.add_argument(
        '--semantic-weight',
        type=float,
        default=0.7,
        help='Peso de similitud semántica (default: 0.7)'
    )
    parser.add_argument(
        '--keyword-weight',
        type=float,
        default=0.3,
        help='Peso de similitud de keywords (default: 0.3)'
    )
    
    args = parser.parse_args(argv)
    
    try:
        recommendations = get_recommendations(
            article_index=args.article_index,
            num_recommendations=args.num_recommendations,
            semantic_weight=args.semantic_weight,
            keyword_weight=args.keyword_weight
        )
        
        print("\n" + "="*80)
        print(f"TOP {len(recommendations)} RECOMENDACIONES")
        print("="*80)
        
        for i, rec in enumerate(recommendations, 1):
            print(f"\n{i}. {rec['title']}")
            print(f"   Autor(es): {rec['author']}")
            print(f"   Año: {rec['year']}")
            print(f"   Score Híbrido: {rec['hybrid_score']:.4f}")
            print(f"   - Semántico: {rec['semantic_score']:.4f}")
            print(f"   - Keywords: {rec['keyword_score']:.4f}")
        
        print("\n" + "="*80)
        print(f"✅ Recomendaciones generadas exitosamente")
        print("="*80)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise


if __name__ == "__main__":
    main()
