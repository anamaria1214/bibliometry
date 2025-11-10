"""
Requerimiento 1: Automatización de descarga y unificación de registros
Scrapers para IEEE, ACM, ScienceDirect y Semantic Scholar
"""

from .scraper import download_semantic_scholar
from .unify_records import unify_bib_files

__all__ = ['download_semantic_scholar', 'unify_bib_files']
