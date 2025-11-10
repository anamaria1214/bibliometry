"""
Sistema de logging centralizado para bibliometry

Proporciona loggers configurados con formato consistente para todos los requerimientos.

Uso:
    from src.utils.logger import get_logger
    
    logger = get_logger(__name__)
    logger.info("Mensaje informativo")
    logger.error("Mensaje de error")
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

# Directorio de logs
PROJECT_ROOT = Path(__file__).parent.parent.parent
LOGS_DIR = PROJECT_ROOT / "data" / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Formato de logs
LOG_FORMAT = "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Colores para terminal (ANSI)
COLORS = {
    'DEBUG': '\033[36m',      # Cyan
    'INFO': '\033[32m',       # Verde
    'WARNING': '\033[33m',    # Amarillo
    'ERROR': '\033[31m',      # Rojo
    'CRITICAL': '\033[35m',   # Magenta
    'RESET': '\033[0m'        # Reset
}


class ColoredFormatter(logging.Formatter):
    """Formatter que añade colores a los logs en terminal"""
    
    def format(self, record):
        # Guardar el levelname original
        levelname = record.levelname
        
        # Añadir color si está disponible
        if sys.stdout.isatty():  # Solo en terminal interactiva
            color = COLORS.get(levelname, COLORS['RESET'])
            record.levelname = f"{color}{levelname}{COLORS['RESET']}"
        
        # Formatear el mensaje
        result = super().format(record)
        
        # Restaurar el levelname original
        record.levelname = levelname
        
        return result


def setup_logger(
    name: str,
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    console: bool = True
) -> logging.Logger:
    """
    Configura un logger con handlers para archivo y consola.
    
    Args:
        name: Nombre del logger (usualmente __name__)
        level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Nombre del archivo de log (opcional)
        console: Si True, también muestra logs en consola
    
    Returns:
        Logger configurado
    
    Ejemplo:
        logger = setup_logger('requerimiento1', level=logging.DEBUG)
        logger.info("Descargando referencias...")
    """
    # Crear logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Evitar duplicados si ya existe
    if logger.handlers:
        return logger
    
    # Formatter estándar (sin colores para archivo)
    file_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    
    # Formatter con colores (para consola)
    console_formatter = ColoredFormatter(LOG_FORMAT, DATE_FORMAT)
    
    # Handler de archivo (si se especifica)
    if log_file:
        log_path = LOGS_DIR / log_file
        file_handler = logging.FileHandler(log_path, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    # Handler de consola
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    return logger


def get_logger(name: str, req_number: Optional[int] = None) -> logging.Logger:
    """
    Obtiene un logger ya configurado o crea uno nuevo.
    
    Args:
        name: Nombre del módulo (usualmente __name__)
        req_number: Número del requerimiento (1-7, opcional)
    
    Returns:
        Logger configurado
    
    Ejemplo:
        logger = get_logger(__name__, req_number=1)
        logger.info("Iniciando scraper...")
    """
    # Prefijo con número de requerimiento
    if req_number:
        logger_name = f"[Req{req_number}] {name}"
        log_file = f"requerimiento{req_number}_{datetime.now().strftime('%Y%m%d')}.log"
    else:
        logger_name = name
        log_file = f"general_{datetime.now().strftime('%Y%m%d')}.log"
    
    # Verificar si ya existe
    existing_logger = logging.getLogger(logger_name)
    if existing_logger.handlers:
        return existing_logger
    
    # Crear nuevo logger
    return setup_logger(
        name=logger_name,
        level=logging.INFO,
        log_file=log_file,
        console=True
    )


def log_execution_time(func):
    """
    Decorador para medir y loggear el tiempo de ejecución de una función.
    
    Uso:
        @log_execution_time
        def mi_funcion():
            # código
    """
    import functools
    import time
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        start_time = time.time()
        
        logger.info(f"Iniciando {func.__name__}...")
        
        try:
            result = func(*args, **kwargs)
            elapsed = time.time() - start_time
            logger.info(f"✅ {func.__name__} completado en {elapsed:.2f}s")
            return result
        
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"❌ {func.__name__} falló después de {elapsed:.2f}s: {e}")
            raise
    
    return wrapper


# Logger por defecto para importaciones rápidas
default_logger = get_logger('bibliometry')
