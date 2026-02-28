"""
Scanner principal: logique de détection multi-timeframes
"""

from typing import Dict, List, Optional, Tuple
from data.twelvedata_client import TwelveDataClient
from data.database import Database
from core.technical import TechnicalAnalyzer
from core.fibonacci import FibonacciCalculator
from core.heiken_ashi import HeikenAshiAnalyzer
from config.settings import (
    SMA_PERIOD,
    FIBONACCI_ZONE_MIN,
    FIBONACCI_ZONE_MAX,
)
from utils.logger import setup_logger

logger = setup_logger(__name__)


class ForexScanner:
    """Scanner Forex avec logique Fibonacci multi-timeframes"""

    def __init__(self, api_client: TwelveDataClient, db: Database):
        """
        Initialiser le scanner
        
        Args:
            api_client: Client Twelve Data
            db: Base de données
        """
        self.api_client = api_client
        self.db = db

    def scan_daily_w1_d1(self, pairs: List[str]) -> Dict[str, str]:
        """
        Scan quotidien W1+D1 pour classifier les paires
        
        Args:
            pairs: Liste des paires
            
        Returns:
            Dict {paire: tendance}
        """
        aligned_pairs = {}
        logger.info(f"Scan quotidien W1+D1 pour {len(pairs)} paires...")

        for symbol in pairs:
            try:
                # Récupérer W1
                w1_data = self.api_client.get_weekly_candles(symbol)
                if not w1_data:
                    logger.warning(f"Pas de données W1 pour {symbol}")
                    continue

                # Récupérer D1
                d1_data = self.api_client.get_daily_candles(symbol)
                if not d1_data:
                    logger.warning(f"Pas de données D1 pour {symbol}")
                    continue

                # Convertir en format standard
                w1_candles = self._convert_candles(w1_data)
                d1_candles = self._convert_candles(d1_data)

                # Calculer SMA200
                w1_sma = TechnicalAnalyzer.calculate_sma(w1_candles, SMA_PERIOD)
                d1_sma = TechnicalAnalyzer.calculate_sma(d1_candles, SMA_PERIOD)

                if not w1_sma or not d1_sma:
                    logger.warning(f"SMA non calculable pour {symbol}")
                    continue

                # Récupérer les prix actuels
                w1_price = float(w1_candles[-1].get("close", 0))
                d1_price = float(d1_candles[-1].get("close", 0))

                # Déterminer la tendance
                w1_trend = TechnicalAnalyzer.determine_trend(w1_price, w1_sma)
                d1_trend = TechnicalAnalyzer.determine_trend(d1_price, d1_sma)

                # Vérifier l'alignement
                if w1_trend == d1_trend and w1_trend != "NEUTRAL":
                    aligned_pairs[symbol] = w1_trend
                    logger.info(f"{symbol}: {w1_trend} (W1+D1 alignés)")
                else:
                    logger.info(f"{symbol}: NEUTRAL (W1: {w1_trend}, D1: {d1_trend})")

                # Sauvegarder le statut
                self.db.update_pair_status(
                    symbol,
                    w1_trend if w1_trend == d1_trend else "NEUTRAL",
                    w1_price,
                    w1_sma,
                    d1_price,
                    d1_sma,
                )

            except Exception as e:
                logger.error(f"Erreur scan {symbol}: {e}")

        logger.info(f"Scan W1+D1 terminé: {len(aligned_pairs)} paires alignées")
        return aligned_pairs

    def scan_hourly_for_signals(
        self,
        symbol: str,
        trend: str,
    ) -> Optional[Dict]:
        """
        Scan H1 pour détecter les signaux
        
        Args:
            symbol: Paire
            trend: Tendance (BULLISH/BEARISH)
            
        Returns:
            Signal détecté ou None
        """
        try:
            # Récupérer les bougies H1
            h1_data = self.api_client.get_hourly_candles(symbol)
            if not h1_data:
                logger.warning(f"Pas de données H1 pour {symbol}")
                return None

            h1_candles = self._convert_candles(h1_data)

            # Convertir en Heiken Ashi
            ha_candles = HeikenAshiAnalyzer.convert_to_heiken_ashi(h1_candles)

            # Récupérer le prix actuel
            current_price = float(h1_candles[-1].get("close", 0))

            if trend == "BULLISH":
                return self._detect_bullish_signal(symbol, h1_candles, ha_candles, current_price)
            elif trend == "BEARISH":
                return self._detect_bearish_signal(symbol, h1_candles, ha_candles, current_price)

        except Exception as e:
            logger.error(f"Erreur scan H1 {symbol}: {e}")

        return None

    def _detect_bullish_signal(
        self,
        symbol: str,
        h1_candles: List[Dict],
        ha_candles: List[Dict],
        current_price: float,
    ) -> Optional[Dict]:
        """Détecter un signal haussier avec jusqu'à 4 Fibonacci"""
        # Calculer jusqu'à 4 Fibonacci
        fibs = FibonacciCalculator.calculate_multiple_fibonacci(h1_candles, mode="bullish", max_count=4)

        if not fibs:
            return None

        # Vérifier si le prix est dans la zone GA d'un des Fibonacci
        price_in_zone = FibonacciCalculator.check_price_in_any_zone(current_price, fibs)
        if not price_in_zone:
            return None

        # Vérifier la confirmation Heiken Ashi
        if not HeikenAshiAnalyzer.is_bullish(ha_candles[-1]):
            return None

        # Calculer les bonus
        rsi_div = TechnicalAnalyzer.detect_rsi_divergence(h1_candles, "bullish")
        supports, resistances = TechnicalAnalyzer.find_support_resistance(h1_candles)
        sr_confluence = TechnicalAnalyzer.check_sr_confluence(current_price, supports, resistances)

        fib_info = price_in_zone.get("fib", {})
        zone_min = price_in_zone.get("zone_min", 0)
        zone_max = price_in_zone.get("zone_max", 0)

        return {
            "symbol": symbol,
            "signal_type": "bullish",
            "price": current_price,
            "fib_index": price_in_zone.get("fib_index"),
            "fib_zone": f"{zone_min:.5f} - {zone_max:.5f}",
            "fib_count": len(fibs),
            "rsi_divergence": rsi_div,
            "sr_confluence": sr_confluence,
            "fibs": fibs,
        }

    def _detect_bearish_signal(
        self,
        symbol: str,
        h1_candles: List[Dict],
        ha_candles: List[Dict],
        current_price: float,
    ) -> Optional[Dict]:
        """Détecter un signal baissier avec jusqu'à 4 Fibonacci"""
        # Calculer jusqu'à 4 Fibonacci
        fibs = FibonacciCalculator.calculate_multiple_fibonacci(h1_candles, mode="bearish", max_count=4)

        if not fibs:
            return None

        # Vérifier si le prix est dans la zone GA d'un des Fibonacci
        price_in_zone = FibonacciCalculator.check_price_in_any_zone(current_price, fibs)
        if not price_in_zone:
            return None

        # Vérifier la confirmation Heiken Ashi
        if not HeikenAshiAnalyzer.is_bearish(ha_candles[-1]):
            return None

        # Calculer les bonus
        rsi_div = TechnicalAnalyzer.detect_rsi_divergence(h1_candles, "bearish")
        supports, resistances = TechnicalAnalyzer.find_support_resistance(h1_candles)
        sr_confluence = TechnicalAnalyzer.check_sr_confluence(current_price, supports, resistances)

        fib_info = price_in_zone.get("fib", {})
        zone_min = price_in_zone.get("zone_min", 0)
        zone_max = price_in_zone.get("zone_max", 0)

        return {
            "symbol": symbol,
            "signal_type": "bearish",
            "price": current_price,
            "fib_index": price_in_zone.get("fib_index"),
            "fib_zone": f"{zone_min:.5f} - {zone_max:.5f}",
            "fib_count": len(fibs),
            "rsi_divergence": rsi_div,
            "sr_confluence": sr_confluence,
            "fibs": fibs,
        }

    @staticmethod
    def _convert_candles(data: List[Dict]) -> List[Dict]:
        """Convertir les données API en format standard"""
        return [
            {
                "timestamp": item.get("datetime"),
                "open": float(item.get("open", 0)),
                "high": float(item.get("high", 0)),
                "low": float(item.get("low", 0)),
                "close": float(item.get("close", 0)),
                "volume": int(item.get("volume", 0)) if item.get("volume") else 0,
            }
            for item in data
        ]
