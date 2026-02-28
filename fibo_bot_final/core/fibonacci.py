"""
Calculs et détection des niveaux Fibonacci
"""

from typing import Dict, List, Tuple
from utils.logger import setup_logger

logger = setup_logger(__name__)


class FibonacciCalculator:
    """Calculs des niveaux Fibonacci"""

    # Niveaux Fibonacci standards
    LEVELS = {
        "level_0": 0.0,
        "level_236": 0.236,
        "level_382": 0.382,
        "level_500": 0.500,
        "level_618": 0.618,
        "level_786": 0.786,
        "level_100": 1.0,
    }

    # Zone de trading (GA)
    ZONE_MIN = 0.500
    ZONE_MAX = 0.618

    @staticmethod
    def calculate_levels(high: float, low: float) -> Dict[str, float]:
        """
        Calculer les niveaux Fibonacci
        
        Args:
            high: Prix haut
            low: Prix bas
            
        Returns:
            Dictionnaire des niveaux
        """
        diff = high - low
        levels = {}

        for name, ratio in FibonacciCalculator.LEVELS.items():
            levels[name] = high - (diff * ratio)

        logger.debug(f"Niveaux Fibonacci calculés: {high} - {low}")
        return levels

    @staticmethod
    def is_price_in_zone(price: float, levels: Dict[str, float]) -> bool:
        """
        Vérifier si le prix est dans la zone GA [0.500, 0.618]
        
        Args:
            price: Prix actuel
            levels: Niveaux Fibonacci
            
        Returns:
            True si dans la zone
        """
        level_500 = levels.get("level_500", 0)
        level_618 = levels.get("level_618", 0)

        # La zone peut être inversée (bearish)
        zone_min = min(level_500, level_618)
        zone_max = max(level_500, level_618)

        in_zone = zone_min <= price <= zone_max
        logger.debug(f"Prix {price} dans zone [{zone_min}, {zone_max}]: {in_zone}")

        return in_zone

    @staticmethod
    def get_zone_boundaries(levels: Dict[str, float]) -> Tuple[float, float]:
        """
        Récupérer les limites de la zone GA
        
        Args:
            levels: Niveaux Fibonacci
            
        Returns:
            Tuple (min, max) de la zone
        """
        level_500 = levels.get("level_500", 0)
        level_618 = levels.get("level_618", 0)

        return (min(level_500, level_618), max(level_500, level_618))

    @staticmethod
    def find_peaks_and_troughs(
        candles: List[Dict],
        lookback: int = 50,
    ) -> Tuple[List[int], List[int]]:
        """
        Trouver les sommets et creux dans les dernières bougies
        
        Args:
            candles: Liste des bougies (format: {high, low, close, ...})
            lookback: Nombre de bougies à analyser
            
        Returns:
            Tuple (indices_sommets, indices_creux) avec indices relatifs à la liste complète
        """
        if len(candles) < 3:
            return [], []

        # Déterminer le point de départ
        start_idx = max(0, len(candles) - lookback)
        recent_candles = candles[start_idx:]
        peaks = []
        troughs = []

        for i in range(1, len(recent_candles) - 1):
            high = recent_candles[i].get("high", 0)
            low = recent_candles[i].get("low", 0)
            prev_high = recent_candles[i - 1].get("high", 0)
            next_high = recent_candles[i + 1].get("high", 0)
            prev_low = recent_candles[i - 1].get("low", 0)
            next_low = recent_candles[i + 1].get("low", 0)

            # Sommet: haut supérieur aux précédent et suivant
            if high > prev_high and high > next_high:
                peaks.append(start_idx + i)

            # Creux: bas inférieur aux précédent et suivant
            if low < prev_low and low < next_low:
                troughs.append(start_idx + i)

        logger.debug(f"Sommets trouvés: {len(peaks)}, Creux trouvés: {len(troughs)}")
        return peaks, troughs

    @staticmethod
    def get_last_peak(candles: List[Dict]) -> Tuple[int, float]:
        """
        Récupérer le dernier sommet
        
        Args:
            candles: Liste des bougies
            
        Returns:
            Tuple (index, prix)
        """
        if not candles:
            return -1, 0

        peaks, _ = FibonacciCalculator.find_peaks_and_troughs(candles)
        if not peaks:
            # Retourner le plus haut des 50 dernières bougies
            recent = candles[-50:]
            max_idx = max(range(len(recent)), key=lambda i: recent[i].get("high", 0))
            return len(candles) - 50 + max_idx, recent[max_idx].get("high", 0)

        last_peak_idx = peaks[-1]
        if last_peak_idx >= len(candles):
            return -1, 0
        return last_peak_idx, candles[last_peak_idx].get("high", 0)

    @staticmethod
    def get_last_trough(candles: List[Dict]) -> Tuple[int, float]:
        """
        Récupérer le dernier creux
        
        Args:
            candles: Liste des bougies
            
        Returns:
            Tuple (index, prix)
        """
        if not candles:
            return -1, 0

        _, troughs = FibonacciCalculator.find_peaks_and_troughs(candles)
        if not troughs:
            # Retourner le plus bas des 50 dernières bougies
            recent = candles[-50:]
            min_idx = min(range(len(recent)), key=lambda i: recent[i].get("low", 0))
            return len(candles) - 50 + min_idx, recent[min_idx].get("low", 0)

        last_trough_idx = troughs[-1]
        if last_trough_idx >= len(candles):
            return -1, 0
        return last_trough_idx, candles[last_trough_idx].get("low", 0)

    @staticmethod
    def calculate_multiple_fibonacci(
        candles: List[Dict],
        mode: str = "bullish",
        max_count: int = 4,
    ) -> List[Dict]:
        """
        Tracer jusqu'à 4 Fibonacci selon le mode
        
        ACHAT (BULLISH):
        - Point A = Dernier sommet (Heiken Ashi rouge→vert)
        - Trouver les 4 derniers creux valides avant ce sommet
        - Tracer 4 Fibonacci : creux_i → sommet
        
        VENTE (BEARISH):
        - Point A = Dernier creux (Heiken Ashi vert→rouge)
        - Trouver les 4 derniers sommets valides avant ce creux
        - Tracer 4 Fibonacci : sommet_i → creux
        
        Args:
            candles: Liste des bougies avec ha_high, ha_low, ha_open, ha_close
            mode: "bullish" ou "bearish"
            max_count: Nombre max de Fibonacci (défaut 4)
            
        Returns:
            Liste de dictionnaires avec les niveaux Fibonacci
        """
        if len(candles) < 10:
            logger.warning("Pas assez de bougies pour calculer les Fibonacci")
            return []

        fibs = []

        if mode.lower() == "bullish":
            # Point A = Dernier sommet (HA rouge→vert)
            point_a_idx, point_a_price = FibonacciCalculator.get_last_peak(candles)
            if point_a_idx < 0:
                return []

            # Trouver les 4 derniers creux AVANT le sommet
            _, troughs = FibonacciCalculator.find_peaks_and_troughs(candles)
            valid_troughs = [t for t in troughs if t < point_a_idx]

            # Prendre les 4 derniers creux valides
            selected_troughs = valid_troughs[-max_count:]

            for i, trough_idx in enumerate(selected_troughs):
                trough_price = candles[trough_idx].get("low", 0)
                levels = FibonacciCalculator.calculate_levels(point_a_price, trough_price)

                fibs.append({
                    "index": i + 1,
                    "mode": "bullish",
                    "point_a": point_a_price,
                    "point_b": trough_price,
                    "point_a_idx": point_a_idx,
                    "point_b_idx": trough_idx,
                    "levels": levels,
                    "zone_min": levels.get("level_500", 0),
                    "zone_max": levels.get("level_618", 0),
                })

            logger.info(f"Bullish: {len(fibs)} Fibonacci tracés (sommet {point_a_price:.5f})")

        elif mode.lower() == "bearish":
            # Point A = Dernier creux (HA vert→rouge)
            point_a_idx, point_a_price = FibonacciCalculator.get_last_trough(candles)
            if point_a_idx < 0:
                return []

            # Trouver les 4 derniers sommets AVANT le creux
            peaks, _ = FibonacciCalculator.find_peaks_and_troughs(candles)
            valid_peaks = [p for p in peaks if p < point_a_idx]

            # Prendre les 4 derniers sommets valides
            selected_peaks = valid_peaks[-max_count:]

            for i, peak_idx in enumerate(selected_peaks):
                peak_price = candles[peak_idx].get("high", 0)
                levels = FibonacciCalculator.calculate_levels(peak_price, point_a_price)

                fibs.append({
                    "index": i + 1,
                    "mode": "bearish",
                    "point_a": peak_price,
                    "point_b": point_a_price,
                    "point_a_idx": peak_idx,
                    "point_b_idx": point_a_idx,
                    "levels": levels,
                    "zone_min": min(levels.get("level_500", 0), levels.get("level_618", 0)),
                    "zone_max": max(levels.get("level_500", 0), levels.get("level_618", 0)),
                })

            logger.info(f"Bearish: {len(fibs)} Fibonacci tracés (creux {point_a_price:.5f})")

        return fibs

    @staticmethod
    def check_price_in_any_zone(
        price: float,
        fibs: List[Dict],
    ) -> Dict:
        """
        Vérifier si le prix est dans la zone GA d'un des Fibonacci
        
        Args:
            price: Prix actuel
            fibs: Liste des Fibonacci
            
        Returns:
            Dict avec {in_zone: bool, fib_index: int, zone_min: float, zone_max: float}
            ou None si pas dans la zone
        """
        for fib in fibs:
            zone_min = fib.get("zone_min", 0)
            zone_max = fib.get("zone_max", 0)

            if zone_min <= price <= zone_max:
                logger.info(f"Prix {price:.5f} dans zone Fib #{fib.get('index')} [{zone_min:.5f}, {zone_max:.5f}]")
                return {
                    "in_zone": True,
                    "fib_index": fib.get("index"),
                    "zone_min": zone_min,
                    "zone_max": zone_max,
                    "fib": fib,
                }

        return None
