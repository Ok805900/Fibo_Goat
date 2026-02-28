"""
Client Twelve Data avec gestion du rate limiting et des crédits
"""

import time
import requests
from typing import Dict, List, Optional
from utils.logger import setup_logger

logger = setup_logger(__name__)


class TwelveDataClient:
    """Client pour l'API Twelve Data avec rate limiting"""

    BASE_URL = "https://api.twelvedata.com"

    def __init__(self, api_key: str):
        """
        Initialiser le client
        
        Args:
            api_key: Clé API Twelve Data
        """
        self.api_key = api_key
        self.requests_per_minute = 0
        self.last_reset_time = time.time()
        self.credits_used = 0
        self.max_credits_daily = 800

    def _check_rate_limit(self):
        """Vérifier et respecter le rate limit (8 req/min)"""
        now = time.time()
        time_since_reset = now - self.last_reset_time

        # Reset le compteur chaque minute
        if time_since_reset > 60:
            self.requests_per_minute = 0
            self.last_reset_time = now

        # Si on a atteint la limite, attendre
        if self.requests_per_minute >= 8:
            wait_time = 60 - time_since_reset
            logger.warning(f"Rate limit atteint. Attente de {wait_time:.1f}s...")
            time.sleep(wait_time)
            self.requests_per_minute = 0
            self.last_reset_time = time.time()

        self.requests_per_minute += 1

    def get_time_series(
        self,
        symbol: str,
        interval: str,
        output_size: int = 100,
    ) -> Optional[Dict]:
        """
        Récupérer les données de série temporelle
        
        Args:
            symbol: Paire (ex: EUR/USD)
            interval: Timeframe (1week, 1day, 1h)
            output_size: Nombre de bougies
            
        Returns:
            Données de série temporelle ou None
        """
        self._check_rate_limit()

        try:
            params = {
                "symbol": symbol,
                "interval": interval,
                "outputsize": min(output_size, 5000),
                "format": "JSON",
                "apikey": self.api_key,
            }

            response = requests.get(
                f"{self.BASE_URL}/time_series",
                params=params,
                timeout=10,
            )
            response.raise_for_status()

            data = response.json()

            if data.get("status") != "ok":
                logger.error(f"Erreur API pour {symbol}: {data.get('message')}")
                return None

            return data

        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur requête pour {symbol}: {e}")
            return None

    def get_weekly_candles(self, symbol: str) -> Optional[List[Dict]]:
        """Récupérer les bougies hebdomadaires"""
        data = self.get_time_series(symbol, "1week", 200)
        return data.get("values", []) if data else None

    def get_daily_candles(self, symbol: str) -> Optional[List[Dict]]:
        """Récupérer les bougies quotidiennes"""
        data = self.get_time_series(symbol, "1day", 200)
        return data.get("values", []) if data else None

    def get_hourly_candles(self, symbol: str) -> Optional[List[Dict]]:
        """Récupérer les bougies horaires"""
        data = self.get_time_series(symbol, "1h", 100)
        return data.get("values", []) if data else None

    def get_credits_remaining(self) -> int:
        """Calculer les crédits restants (estimation)"""
        return max(0, self.max_credits_daily - self.credits_used)

    def log_credit_usage(self, amount: int):
        """Enregistrer l'utilisation de crédits"""
        self.credits_used += amount
        logger.info(f"Crédits utilisés: {self.credits_used}/{self.max_credits_daily}")
