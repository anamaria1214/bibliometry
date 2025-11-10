"""
Requerimiento 7: Sistema de Recomendación Híbrido

Exportaciones:
    - get_recommendations: Función principal para obtener recomendaciones
    - main: Función CLI para uso desde terminal o menu.py
"""

from .recommender import get_recommendations, main

__all__ = ['get_recommendations', 'main']
