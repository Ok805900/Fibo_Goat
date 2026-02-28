"""
Handlers des commandes Telegram
"""

from telegram import Update
from telegram.ext import ContextTypes
from data.database import Database
from utils.logger import setup_logger

logger = setup_logger(__name__)


class CommandHandlers:
    """Handlers des commandes Telegram"""

    def __init__(self, db: Database):
        """
        Initialiser les handlers
        
        Args:
            db: Base de données
        """
        self.db = db

    async def handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Commande /start"""
        try:
            message = """
Bienvenue dans le Forex Fibonacci Bot! 🤖

Ce bot analyse automatiquement 14 paires Forex avec une stratégie Fibonacci multi-timeframes.

Commandes disponibles:
/status - Statut des paires alignées et crédits API
/pairs - Statut détaillé des 14 paires
/history - Derniers signaux (24h)
/stats - Performance (weekend uniquement)

Le bot scanne automatiquement:
• Daily à 00:00 UTC (W1+D1)
• Toutes les heures (H1)

Vous recevrez des notifications pour chaque signal détecté.
            """
            await update.message.reply_text(message, parse_mode="HTML")
            logger.info(f"Commande /start de {update.effective_user.id}")

        except Exception as e:
            logger.error(f"Erreur /start: {e}")
            await update.message.reply_text("Erreur lors du traitement de la commande.")

    async def handle_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Commande /status"""
        try:
            pair_statuses = self.db.get_all_pair_statuses()

            bullish = [p["symbol"] for p in pair_statuses if p["trend"] == "BULLISH"]
            bearish = [p["symbol"] for p in pair_statuses if p["trend"] == "BEARISH"]
            neutral = [p["symbol"] for p in pair_statuses if p["trend"] == "NEUTRAL"]

            message = f"""
📊 Statut des paires alignées

🟢 BULLISH ({len(bullish)}):
{", ".join(bullish) if bullish else "Aucune"}

🔴 BEARISH ({len(bearish)}):
{", ".join(bearish) if bearish else "Aucune"}

⚪ NEUTRAL ({len(neutral)}):
{", ".join(neutral) if neutral else "Aucune"}

💾 Crédits API: ~700/800 (estimation)
            """

            await update.message.reply_text(message, parse_mode="HTML")
            logger.info(f"Commande /status de {update.effective_user.id}")

        except Exception as e:
            logger.error(f"Erreur /status: {e}")
            await update.message.reply_text("Erreur lors du traitement de la commande.")

    async def handle_pairs(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Commande /pairs"""
        try:
            pair_statuses = self.db.get_all_pair_statuses()

            if not pair_statuses:
                await update.message.reply_text("Aucun statut de paire disponible.")
                return

            message = "📋 Statut détaillé des 14 paires\n\n"

            for status in pair_statuses:
                symbol = status.get("symbol", "")
                trend = status.get("trend", "NEUTRAL")
                w1_price = status.get("w1_price", 0)
                w1_sma = status.get("w1_sma200", 0)
                d1_price = status.get("d1_price", 0)
                d1_sma = status.get("d1_sma200", 0)

                emoji = "🟢" if trend == "BULLISH" else "🔴" if trend == "BEARISH" else "⚪"

                message += f"""
{emoji} {symbol} - {trend}
   W1: {w1_price:.5f} vs SMA {w1_sma:.5f}
   D1: {d1_price:.5f} vs SMA {d1_sma:.5f}
"""

            await update.message.reply_text(message, parse_mode="HTML")
            logger.info(f"Commande /pairs de {update.effective_user.id}")

        except Exception as e:
            logger.error(f"Erreur /pairs: {e}")
            await update.message.reply_text("Erreur lors du traitement de la commande.")

    async def handle_history(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Commande /history"""
        try:
            signals = self.db.get_signals_24h()

            if not signals:
                await update.message.reply_text("Aucun signal détecté dans les 24 dernières heures.")
                return

            message = "📜 Derniers signaux (24h)\n\n"

            for signal in signals[:10]:  # Limiter à 10
                symbol = signal.get("symbol", "")
                signal_type = signal.get("signal_type", "").upper()
                price = signal.get("price", 0)
                fib_level = signal.get("fib_level", "")
                created_at = signal.get("created_at", "")

                emoji = "📈" if signal_type == "BULLISH" else "📉"

                message += f"{emoji} {symbol} {signal_type} @ {price:.5f} ({fib_level})\n   {created_at}\n\n"

            await update.message.reply_text(message, parse_mode="HTML")
            logger.info(f"Commande /history de {update.effective_user.id}")

        except Exception as e:
            logger.error(f"Erreur /history: {e}")
            await update.message.reply_text("Erreur lors du traitement de la commande.")

    async def handle_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Commande /stats (weekend uniquement)"""
        try:
            from datetime import datetime

            today = datetime.utcnow().weekday()
            is_weekend = today >= 5  # 5 = samedi, 6 = dimanche

            if not is_weekend:
                await update.message.reply_text("Les statistiques sont disponibles uniquement le weekend.")
                return

            signals = self.db.get_signals_24h()

            if not signals:
                await update.message.reply_text("Aucun signal détecté.")
                return

            bullish_count = sum(1 for s in signals if s.get("signal_type") == "bullish")
            bearish_count = sum(1 for s in signals if s.get("signal_type") == "bearish")

            message = f"""
📊 Statistiques de performance (Weekend)

Total signaux: {len(signals)}
🟢 Haussiers: {bullish_count}
🔴 Baissiers: {bearish_count}

Taux de confirmation: ~{(len(signals) / max(1, len(signals))) * 100:.1f}%
            """

            await update.message.reply_text(message, parse_mode="HTML")
            logger.info(f"Commande /stats de {update.effective_user.id}")

        except Exception as e:
            logger.error(f"Erreur /stats: {e}")
            await update.message.reply_text("Erreur lors du traitement de la commande.")

    async def handle_error(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Gestionnaire d'erreurs"""
        logger.error(f"Erreur: {context.error}")
