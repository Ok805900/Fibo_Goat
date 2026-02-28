"""
Calculs techniques: SMA, RSI, Support/Résistance
"""

from typing import Dict, List, Tuple, Optional
from utils.logger import setup_logger

logger = setup_logger(__name__)


class TechnicalAnalyzer:
    """Analyse technique"""

    @staticmethod
    def calculate_sma(candles: List[Dict], period: int) -> Optional[float]:
        """
        Calculer la SMA (Simple Moving Average)
        
        Args:
            candles: Liste des bougies
            period: Période (ex: 200)
            
        Returns:
            Valeur SMA ou None
        """
        if len(candles) < period:
            return None

        closes = [float(c.get("close", 0)) for c in candles[-period:]]
        sma = sum(closes) / period

        logger.debug(f"SMA{period} calculée: {sma}")
        return sma

    @staticmethod
    def calculate_rsi(candles: List[Dict], period: int = 14) -> Optional[float]:
        """
        Calculer le RSI (Relative Strength Index)
        
        Args:
            candles: Liste des bougies
            period: Période (par défaut 14)
            
        Returns:
            Valeur RSI ou None
        """
        if len(candles) < period + 1:
            return None

        closes = [float(c.get("close", 0)) for c in candles]
        deltas = [closes[i] - closes[i - 1] for i in range(1, len(closes))]

        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]

        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period

        if avg_loss == 0:
            rsi = 100 if avg_gain > 0 else 0
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))

        logger.debug(f"RSI{period} calculée: {rsi}")
        return rsi

    @staticmethod
    def detect_rsi_divergence(
        candles: List[Dict],
        signal_type: str,
        period: int = 14,
    ) -> bool:
        """
        Détecter une divergence RSI
        
        Args:
            candles: Liste des bougies
            signal_type: Type de signal (bullish/bearish)
            period: Période RSI
            
        Returns:
            True si divergence détectée
        """
        if len(candles) < period + 10:
            return False

        # Calculer RSI pour les 10 dernières bougies
        rsi_values = []
        for i in range(10):
            rsi = TechnicalAnalyzer.calculate_rsi(candles[:-10 + i], period)
            if rsi is not None:
                rsi_values.append(rsi)

        if len(rsi_values) < 2:
            return False

        # Divergence haussière: prix bas mais RSI haut
        if signal_type == "bullish":
            prices = [float(c.get("low", 0)) for c in candles[-10:]]
            if prices[-1] < prices[-2] and rsi_values[-1] > rsi_values[-2]:
                logger.debug("Divergence RSI haussière détectée")
                return True

        # Divergence baissière: prix haut mais RSI bas
        elif signal_type == "bearish":
            prices = [float(c.get("high", 0)) for c in candles[-10:]]
            if prices[-1] > prices[-2] and rsi_values[-1] < rsi_values[-2]:
                logger.debug("Divergence RSI baissière détectée")
                return True

        return False

    @staticmethod
    def find_support_resistance(
        candles: List[Dict],
        lookback: int = 50,
    ) -> Tuple[List[float], List[float]]:
        """
        Trouver les niveaux de support et résistance
        
        Args:
            candles: Liste des bougies
            lookback: Nombre de bougies à analyser
            
        Returns:
            Tuple (supports, resistances)
        """
        if len(candles) < lookback:
            return [], []

        recent_candles = candles[-lookback:]
        highs = [float(c.get("high", 0)) for c in recent_candles]
        lows = [float(c.get("low", 0)) for c in recent_candles]

        # Trouver les points hauts et bas locaux
        resistances = []
        supports = []

        for i in range(1, len(recent_candles) - 1):
            if highs[i] > highs[i - 1] and highs[i] > highs[i + 1]:
                resistances.append(highs[i])

            if lows[i] < lows[i - 1] and lows[i] < lows[i + 1]:
                supports.append(lows[i])

        # Trier et dédupliquer (regrouper les niveaux proches)
        resistances = sorted(list(set(resistances)), reverse=True)
        supports = sorted(list(set(supports)))

        logger.debug(f"S/R trouvés: {len(supports)} supports, {len(resistances)} résistances")
        return supports, resistances

    @staticmethod
    def check_sr_confluence(
        price: float,
        supports: List[float],
        resistances: List[float],
        tolerance: float = 0.001,  # 0.1%
    ) -> bool:
        """
        Vérifier si le prix est proche d'un niveau S/R
        
        Args:
            price: Prix actuel
            supports: Niveaux de support
            resistances: Niveaux de résistance
            tolerance: Tolérance en pourcentage
            
        Returns:
            True si confluence détectée
        """
        tolerance_amount = price * tolerance

        # Vérifier supports
        for support in supports:
            if abs(price - support) <= tolerance_amount:
                logger.debug(f"Confluence support détectée: {support}")
                return True

        # Vérifier résistances
        for resistance in resistances:
            if abs(price - resistance) <= tolerance_amount:
                logger.debug(f"Confluence résistance détectée: {resistance}")
                return True

        return False

    @staticmethod
    def determine_trend(price: float, sma: float) -> str:
        """
        Déterminer la tendance basée sur SMA
        
        Args:
            price: Prix actuel
            sma: Valeur SMA
            
        Returns:
            "BULLISH", "BEARISH", ou "NEUTRAL"
        """
        if price > sma:
            return "BULLISH"
        elif price < sma:
            return "BEARISH"
        else:
            return "NEUTRAL"
