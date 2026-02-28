"""
Gestion des variables d'environnement et secrets
"""

import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()


class Secrets:
    """Classe pour accéder aux variables d'environnement"""

    @staticmethod
    def get_telegram_token() -> str:
        """Récupérer le token Telegram"""
        token = os.getenv("TELEGRAM_TOKEN_FIBOBOT")
        if not token:
            raise ValueError("TELEGRAM_TOKEN_FIBOBOT n'est pas défini")
        return token

    @staticmethod
    def get_twelvedata_api_key() -> str:
        """Récupérer la clé API Twelve Data"""
        api_key = os.getenv("TWELVEDATA_API_KEY_FIBOBOT")
        if not api_key:
            raise ValueError("TWELVEDATA_API_KEY_FIBOBOT n'est pas défini")
        return api_key

    @staticmethod
    def get_log_level() -> str:
        """Récupérer le niveau de log"""
        return os.getenv("LOG_LEVEL", "INFO")

    @staticmethod
    def get_timezone() -> str:
        """Récupérer la timezone"""
        return os.getenv("TIMEZONE", "UTC")

    @staticmethod
    def get_scan_time() -> str:
        """Récupérer l'heure du scan quotidien"""
        return os.getenv("SCAN_TIME_DAILY", "00:00")
