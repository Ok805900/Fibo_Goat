"""
Conversion et analyse des bougies Heiken Ashi
"""

from typing import Dict, List
from utils.logger import setup_logger

logger = setup_logger(__name__)


class HeikenAshiAnalyzer:
    """Analyse des bougies Heiken Ashi"""

    @staticmethod
    def convert_to_heiken_ashi(candles: List[Dict]) -> List[Dict]:
        """
        Convertir les bougies standards en Heiken Ashi
        
        Args:
            candles: Liste des bougies standards
            
        Returns:
            Liste des bougies Heiken Ashi
        """
        if not candles:
            return []

        ha_candles = []
        prev_ha_open = 0
        prev_ha_close = 0

        for i, candle in enumerate(candles):
            open_price = float(candle.get("open", 0))
            high = float(candle.get("high", 0))
            low = float(candle.get("low", 0))
            close = float(candle.get("close", 0))

            # Heiken Ashi Close = moyenne OHLC
            ha_close = (open_price + high + low + close) / 4

            # Heiken Ashi Open = moyenne du HA open/close précédent
            if i == 0:
                ha_open = (open_price + close) / 2
            else:
                ha_open = (prev_ha_open + prev_ha_close) / 2

            # Heiken Ashi High/Low
            ha_high = max(high, ha_open, ha_close)
            ha_low = min(low, ha_open, ha_close)

            ha_candles.append({
                "timestamp": candle.get("timestamp"),
                "open": open_price,
                "high": high,
                "low": low,
                "close": close,
                "ha_open": ha_open,
                "ha_high": ha_high,
                "ha_low": ha_low,
                "ha_close": ha_close,
            })

            prev_ha_open = ha_open
            prev_ha_close = ha_close

        logger.debug(f"Conversion Heiken Ashi: {len(candles)} bougies")
        return ha_candles

    @staticmethod
    def is_bullish(ha_candle: Dict) -> bool:
        """
        Vérifier si une bougie Heiken Ashi est haussière
        
        Args:
            ha_candle: Bougie Heiken Ashi
            
        Returns:
            True si haussière (HA close > HA open)
        """
        return ha_candle.get("ha_close", 0) > ha_candle.get("ha_open", 0)

    @staticmethod
    def is_bearish(ha_candle: Dict) -> bool:
        """
        Vérifier si une bougie Heiken Ashi est baissière
        
        Args:
            ha_candle: Bougie Heiken Ashi
            
        Returns:
            True si baissière (HA close < HA open)
        """
        return ha_candle.get("ha_close", 0) < ha_candle.get("ha_open", 0)

    @staticmethod
    def detect_color_change(
        prev_ha_candle: Dict,
        curr_ha_candle: Dict,
    ) -> str:
        """
        Détecter le changement de couleur Heiken Ashi
        
        Args:
            prev_ha_candle: Bougie Heiken Ashi précédente
            curr_ha_candle: Bougie Heiken Ashi actuelle
            
        Returns:
            "red_to_green", "green_to_red", ou "no_change"
        """
        prev_bullish = HeikenAshiAnalyzer.is_bullish(prev_ha_candle)
        curr_bullish = HeikenAshiAnalyzer.is_bullish(curr_ha_candle)

        if not prev_bullish and curr_bullish:
            return "red_to_green"
        elif prev_bullish and not curr_bullish:
            return "green_to_red"
        else:
            return "no_change"

    @staticmethod
    def is_peak_confirmed(
        candles: List[Dict],
        peak_idx: int,
    ) -> bool:
        """
        Vérifier si un sommet est confirmé par Heiken Ashi
        (changement de rouge à vert)
        
        Args:
            candles: Liste des bougies Heiken Ashi
            peak_idx: Index du sommet
            
        Returns:
            True si confirmé
        """
        if peak_idx < 1 or peak_idx >= len(candles):
            return False

        prev_candle = candles[peak_idx - 1]
        curr_candle = candles[peak_idx]

        change = HeikenAshiAnalyzer.detect_color_change(prev_candle, curr_candle)
        return change == "red_to_green"

    @staticmethod
    def is_trough_confirmed(
        candles: List[Dict],
        trough_idx: int,
    ) -> bool:
        """
        Vérifier si un creux est confirmé par Heiken Ashi
        (changement de vert à rouge)
        
        Args:
            candles: Liste des bougies Heiken Ashi
            trough_idx: Index du creux
            
        Returns:
            True si confirmé
        """
        if trough_idx < 1 or trough_idx >= len(candles):
            return False

        prev_candle = candles[trough_idx - 1]
        curr_candle = candles[trough_idx]

        change = HeikenAshiAnalyzer.detect_color_change(prev_candle, curr_candle)
        return change == "green_to_red"

    @staticmethod
    def is_body_outside_zone(
        ha_candle: Dict,
        zone_min: float,
        zone_max: float,
    ) -> bool:
        """
        Vérifier si le corps de la bougie est hors de la zone
        (cassure de zone)
        
        Args:
            ha_candle: Bougie Heiken Ashi
            zone_min: Limite basse de la zone
            zone_max: Limite haute de la zone
            
        Returns:
            True si le corps est hors de la zone
        """
        ha_open = ha_candle.get("ha_open", 0)
        ha_close = ha_candle.get("ha_close", 0)

        body_min = min(ha_open, ha_close)
        body_max = max(ha_open, ha_close)

        # Corps hors zone si complètement au-dessus ou au-dessous
        is_above = body_min > zone_max
        is_below = body_max < zone_min

        return is_above or is_below
