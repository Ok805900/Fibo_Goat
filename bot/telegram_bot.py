"""
Gestionnaire du Bot Telegram - Compatible python-telegram-bot v20+
"""

from typing import Dict, List
from telegram import BotCommand
from utils.logger import setup_logger

logger = setup_logger(__name__)


class FiboBotManager:
    """Gestionnaire du bot Telegram"""

    def __init__(self):
        """Initialiser le gestionnaire"""
        self.application = None

    async def setup(self, application):
        """Configurer le bot"""
        try:
            self.application = application

            # Enregistrer les commandes
            await self.application.bot.set_my_commands([
                BotCommand("start", "Démarrer le bot"),
                BotCommand("status", "Statut des paires alignées"),
                BotCommand("pairs", "Statut détaillé des 14 paires"),
                BotCommand("history", "Derniers signaux (24h)"),
                BotCommand("stats", "Performance (weekend uniquement)"),
            ])

            logger.info("Bot Telegram configuré avec succès (v20+)")
            return True

        except Exception as e:
            logger.error(f"Erreur configuration bot: {e}", exc_info=True)
            return False

    async def send_message(self, chat_id: int, message: str):
        """
        Envoyer un message
        
        Args:
            chat_id: ID du chat
            message: Message à envoyer
        """
        try:
            if self.application:
                await self.application.bot.send_message(
                    chat_id=chat_id, 
                    text=message, 
                    parse_mode="HTML"
                )
                logger.info(f"Message envoyé à {chat_id}")
            else:
                logger.error("Bot non initialisé")
        except Exception as e:
            logger.error(f"Erreur envoi message: {e}", exc_info=True)

    async def send_signal_notification(
        self,
        chat_id: int,
        signal: Dict,
    ):
        """
        Envoyer une notification de signal
        
        Args:
            chat_id: ID du chat
            signal: Données du signal
        """
        try:
            symbol = signal.get("symbol", "")
            signal_type = signal.get("signal_type", "").upper()
            price = signal.get("price", 0)
            fib_zone = signal.get("fib_zone", "")
            rsi_div = signal.get("rsi_divergence", False)
            sr_conf = signal.get("sr_confluence", False)

            emoji_signal = "📊" if signal_type == "BULLISH" else "📉"
            emoji_rsi = "🟢" if rsi_div else "⚪"
            emoji_sr = "🟢" if sr_conf else "⚪"

            message = f"""
{emoji_signal} <b>[{symbol}] - SETUP {signal_type}</b>
├─ Filtres W1/D1: ✅ {signal_type}
├─ GA: 0.500-0.618 [{fib_zone}]
├─ Heiken Ashi: {'Haussier' if signal_type == 'BULLISH' else 'Baissier'} ✅
├─ Prix: {price:.5f}
├─ RSI: Divergence {emoji_rsi}
└─ S/R: Confluence {emoji_sr}
            """

            await self.send_message(chat_id, message)
        except Exception as e:
            logger.error(f"Erreur notification signal: {e}", exc_info=True)

    async def send_price_in_zone_notification(
        self,
        chat_id: int,
        symbol: str,
        price: float,
        zone: str,
        signal_type: str,
    ):
        """
        Envoyer une notification "Prix dans GA"
        
        Args:
            chat_id: ID du chat
            symbol: Paire
            price: Prix actuel
            zone: Zone Fibonacci
            signal_type: Type de signal
        """
        try:
            direction = "ACHAT" if signal_type == "BULLISH" else "VENTE"

            message = f"""
⚠️ <b>[{symbol}] - Prix dans GA 0.500-0.618</b>
Zone: {zone} | Prix: {price:.5f}
Direction: {direction} | Status: En attente confirmation...
            """

            await self.send_message(chat_id, message)
        except Exception as e:
            logger.error(f"Erreur notification zone: {e}", exc_info=True)

    async def send_zone_broken_notification(
        self,
        chat_id: int,
        symbol: str,
        price: float,
    ):
        """
        Envoyer une notification "GA cassée"
        
        Args:
            chat_id: ID du chat
            symbol: Paire
            price: Prix actuel
        """
        try:
            message = f"""
❌ <b>[{symbol}] - GA cassée</b>
Zone invalidée | Prix: {price:.5f} | Setup annulé
            """

            await self.send_message(chat_id, message)
        except Exception as e:
            logger.error(f"Erreur notification cassée: {e}", exc_info=True)

    async def send_daily_summary(
        self,
        chat_id: int,
        bullish_pairs: List[str],
        bearish_pairs: List[str],
        neutral_pairs: List[str],
    ):
        """
        Envoyer le résumé quotidien
        
        Args:
            chat_id: ID du chat
            bullish_pairs: Paires haussières
            bearish_pairs: Paires baissières
            neutral_pairs: Paires neutres
        """
        try:
            from datetime import datetime

            date_str = datetime.utcnow().strftime("%Y-%m-%d")

            bullish_str = ", ".join(bullish_pairs) if bullish_pairs else "Aucune"
            bearish_str = ", ".join(bearish_pairs) if bearish_pairs else "Aucune"

            message = f"""
📅 <b>[{date_str}] - Paires alignées</b>
🟢 BULLISH: {bullish_str} ({len(bullish_pairs)})
🔴 BEARISH: {bearish_str} ({len(bearish_pairs)})
⚪ NEUTRE: {len(neutral_pairs)} paires
Prochains scans: {", ".join(bullish_pairs + bearish_pairs) if (bullish_pairs or bearish_pairs) else "Aucun"}
            """

            await self.send_message(chat_id, message)
        except Exception as e:
            logger.error(f"Erreur résumé quotidien: {e}", exc_info=True)

    async def send_heartbeat(self, chat_id: int):
        """
        Envoyer un message de vie du bot
        
        Args:
            chat_id: ID du chat
        """
        try:
            from datetime import datetime

            time_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
            message = f"🤖 Bot actif - {time_str}"

            await self.send_message(chat_id, message)
        except Exception as e:
            logger.error(f"Erreur heartbeat: {e}", exc_info=True)
