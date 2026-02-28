"""
Configuration des paramètres du bot Fibonacci
"""

# 14 paires Forex
PAIRS = [
    "EUR/USD",
    "GBP/USD",
    "USD/JPY",
    "USD/CHF",
    "AUD/USD",
    "USD/CAD",
    "NZD/USD",
    "EUR/GBP",
    "EUR/JPY",
    "GBP/JPY",
    "AUD/JPY",
    "EUR/CHF",
    "GBP/CHF",
    "CAD/JPY",
]

# Timeframes
TIMEFRAMES = {
    "weekly": "1week",
    "daily": "1day",
    "hourly": "1h",
}

# Paramètres techniques
SMA_PERIOD = 200
RSI_PERIOD = 14
FIBONACCI_LEVELS = {
    "level_0": 0.0,
    "level_236": 0.236,
    "level_382": 0.382,
    "level_500": 0.500,
    "level_618": 0.618,
    "level_786": 0.786,
    "level_100": 1.0,
}

# Zone de trading (GA - Zone d'Action)
FIBONACCI_ZONE_MIN = 0.500
FIBONACCI_ZONE_MAX = 0.618

# Limites API Twelve Data
TWELVEDATA_CREDITS_DAILY_LIMIT = 800
TWELVEDATA_REQUESTS_PER_MINUTE = 8
TWELVEDATA_CREDITS_PER_REQUEST = 1

# Budget optimisé
BUDGET_W1_D1_SCAN = 112  # 14 paires * 4 requêtes (W1 + D1 prix + SMA)
BUDGET_H1_SCAN = 14  # 14 paires max
BUDGET_DAILY_TARGET = 500

# Scans
SCAN_TIME_DAILY = "00:00"  # UTC
SCAN_INTERVAL_HOURLY = 1  # heure

# Heiken Ashi
HEIKEN_ASHI_LOOKBACK = 50

# Support/Résistance
SR_LOOKBACK = 50

# Logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Timezone
TIMEZONE = "UTC"

# Commandes Telegram disponibles
TELEGRAM_COMMANDS = {
    "start": "Démarrer le bot",
    "status": "Statut des paires alignées et crédits API",
    "pairs": "Statut détaillé des 14 paires",
    "history": "Derniers signaux (24h)",
    "stats": "Performance (weekend uniquement)",
}

# Messages
HEARTBEAT_INTERVAL = 6  # heures
