"""
Logger pour le bot Fibonacci
"""

import logging
import logging.handlers
import os
from config.settings import LOG_FORMAT, LOG_LEVEL


def setup_logger(name: str) -> logging.Logger:
    """
    Configurer un logger avec rotation de fichiers
    
    Args:
        name: Nom du logger
        
    Returns:
        Logger configuré
    """
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)

    # Créer le répertoire logs s'il n'existe pas
    if not os.path.exists("logs"):
        os.makedirs("logs")

    # Handler fichier avec rotation
    file_handler = logging.handlers.RotatingFileHandler(
        "logs/fibo_bot.log",
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
    )
    file_handler.setLevel(LOG_LEVEL)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))

    # Handler console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(LOG_LEVEL)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT))

    # Ajouter les handlers
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger
