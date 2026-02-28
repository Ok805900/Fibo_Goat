"""
Base de données SQLite pour l'historique des signaux
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
from utils.logger import setup_logger

logger = setup_logger(__name__)


class Database:
    """Gestion de la base de données SQLite"""

    def __init__(self, db_path: str = "fibo_bot.db"):
        """
        Initialiser la base de données
        
        Args:
            db_path: Chemin du fichier SQLite
        """
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialiser les tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Table des signaux
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS signals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    timeframe TEXT NOT NULL,
                    signal_type TEXT NOT NULL,
                    price REAL NOT NULL,
                    fib_level TEXT NOT NULL,
                    heiken_ashi_confirmed BOOLEAN NOT NULL,
                    rsi_divergence BOOLEAN,
                    sr_confluence BOOLEAN,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Table des statuts de paires
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pair_status (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT UNIQUE NOT NULL,
                    trend TEXT NOT NULL,
                    w1_price REAL,
                    w1_sma200 REAL,
                    d1_price REAL,
                    d1_sma200 REAL,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Table des zones actives
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS active_zones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    zone_type TEXT NOT NULL,
                    high REAL NOT NULL,
                    low REAL NOT NULL,
                    level_500 REAL NOT NULL,
                    level_618 REAL NOT NULL,
                    status TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()
            conn.close()
            logger.info(f"Base de données initialisée: {self.db_path}")

        except sqlite3.Error as e:
            logger.error(f"Erreur initialisation BD: {e}")

    def save_signal(
        self,
        symbol: str,
        timeframe: str,
        signal_type: str,
        price: float,
        fib_level: str,
        heiken_ashi_confirmed: bool,
        rsi_divergence: bool = False,
        sr_confluence: bool = False,
    ) -> bool:
        """
        Sauvegarder un signal
        
        Args:
            symbol: Paire
            timeframe: Timeframe
            signal_type: Type de signal (bullish/bearish)
            price: Prix
            fib_level: Niveau Fibonacci
            heiken_ashi_confirmed: Confirmation Heiken Ashi
            rsi_divergence: Divergence RSI
            sr_confluence: Confluence S/R
            
        Returns:
            True si succès
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO signals 
                (symbol, timeframe, signal_type, price, fib_level, heiken_ashi_confirmed, rsi_divergence, sr_confluence)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (symbol, timeframe, signal_type, price, fib_level, heiken_ashi_confirmed, rsi_divergence, sr_confluence))

            conn.commit()
            conn.close()
            return True

        except sqlite3.Error as e:
            logger.error(f"Erreur sauvegarde signal: {e}")
            return False

    def get_signals_24h(self, symbol: Optional[str] = None) -> List[Dict]:
        """
        Récupérer les signaux des 24 dernières heures
        
        Args:
            symbol: Paire (optionnel)
            
        Returns:
            Liste des signaux
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            if symbol:
                cursor.execute("""
                    SELECT * FROM signals
                    WHERE symbol = ? AND created_at > datetime('now', '-1 day')
                    ORDER BY created_at DESC
                """, (symbol,))
            else:
                cursor.execute("""
                    SELECT * FROM signals
                    WHERE created_at > datetime('now', '-1 day')
                    ORDER BY created_at DESC
                """)

            rows = cursor.fetchall()
            conn.close()

            return [dict(row) for row in rows]

        except sqlite3.Error as e:
            logger.error(f"Erreur lecture signaux: {e}")
            return []

    def update_pair_status(
        self,
        symbol: str,
        trend: str,
        w1_price: float,
        w1_sma200: float,
        d1_price: float,
        d1_sma200: float,
    ) -> bool:
        """
        Mettre à jour le statut d'une paire
        
        Args:
            symbol: Paire
            trend: Tendance (BULLISH/BEARISH/NEUTRAL)
            w1_price: Prix Weekly
            w1_sma200: SMA200 Weekly
            d1_price: Prix Daily
            d1_sma200: SMA200 Daily
            
        Returns:
            True si succès
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT OR REPLACE INTO pair_status
                (symbol, trend, w1_price, w1_sma200, d1_price, d1_sma200, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (symbol, trend, w1_price, w1_sma200, d1_price, d1_sma200))

            conn.commit()
            conn.close()
            return True

        except sqlite3.Error as e:
            logger.error(f"Erreur mise à jour statut paire: {e}")
            return False

    def get_pair_status(self, symbol: str) -> Optional[Dict]:
        """
        Récupérer le statut d'une paire
        
        Args:
            symbol: Paire
            
        Returns:
            Statut de la paire ou None
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM pair_status WHERE symbol = ?", (symbol,))
            row = cursor.fetchone()
            conn.close()

            return dict(row) if row else None

        except sqlite3.Error as e:
            logger.error(f"Erreur lecture statut paire: {e}")
            return None

    def get_all_pair_statuses(self) -> List[Dict]:
        """Récupérer le statut de toutes les paires"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM pair_status ORDER BY symbol")
            rows = cursor.fetchall()
            conn.close()

            return [dict(row) for row in rows]

        except sqlite3.Error as e:
            logger.error(f"Erreur lecture statuts paires: {e}")
            return []
