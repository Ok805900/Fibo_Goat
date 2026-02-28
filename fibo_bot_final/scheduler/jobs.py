"""
Jobs du scheduler pour les scans automatiques
"""

from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
import pytz

from config.settings import PAIRS, SCAN_TIME_DAILY, TIMEZONE
from core.scanner import ForexScanner
from bot.telegram_bot import FiboBotManager
from data.twelvedata_client import TwelveDataClient
from data.database import Database
from utils.logger import setup_logger

logger = setup_logger(__name__)


class SchedulerManager:
    """Gestionnaire du scheduler"""

    def __init__(
        self,
        api_client: TwelveDataClient,
        db: Database,
        application,
        chat_id: int,
    ):
        """
        Initialiser le scheduler
        
        Args:
            api_client: Client Twelve Data
            db: Base de données
            bot_manager: Gestionnaire du bot
            chat_id: ID du chat pour les notifications
        """
        self.api_client = api_client
        self.db = db
        self.application = application
        self.chat_id = chat_id
        self.scanner = ForexScanner(api_client, db)
        self.scheduler = AsyncIOScheduler(timezone=pytz.timezone(TIMEZONE))
        self.aligned_pairs = {}

    def setup(self):
        """Configurer les jobs"""
        try:
            # Job: Scan quotidien W1+D1 à 00:00 UTC
            scan_time_parts = SCAN_TIME_DAILY.split(":")
            hour = int(scan_time_parts[0])
            minute = int(scan_time_parts[1]) if len(scan_time_parts) > 1 else 0

            self.scheduler.add_job(
                self.job_daily_scan,
                CronTrigger(hour=hour, minute=minute, timezone=pytz.UTC),
                id="daily_scan",
                name="Scan quotidien W1+D1",
            )

            # Job: Scan H1 toutes les heures
            self.scheduler.add_job(
                self.job_hourly_scan,
                CronTrigger(minute=0, timezone=pytz.UTC),
                id="hourly_scan",
                name="Scan H1 horaire",
            )

            # Job: Heartbeat toutes les 6 heures
            self.scheduler.add_job(
                self.job_heartbeat,
                IntervalTrigger(hours=6),
                id="heartbeat",
                name="Heartbeat",
            )

            logger.info("Scheduler configuré avec succès")
            return self.scheduler

        except Exception as e:
            logger.error(f"Erreur configuration scheduler: {e}")
            raise

    async def job_daily_scan(self):
        """Job: Scan quotidien W1+D1"""
        try:
            logger.info("🔄 Démarrage du scan quotidien W1+D1...")

            # Scanner les 14 paires
            self.aligned_pairs = self.scanner.scan_daily_w1_d1(PAIRS)

            bullish_pairs = [p for p, t in self.aligned_pairs.items() if t == "BULLISH"]
            bearish_pairs = [p for p, t in self.aligned_pairs.items() if t == "BEARISH"]
            neutral_count = len(PAIRS) - len(bullish_pairs) - len(bearish_pairs)

            logger.info(f"Résultats: {len(bullish_pairs)} BULLISH, {len(bearish_pairs)} BEARISH, {neutral_count} NEUTRAL")

            # Envoyer le résumé quotidien
            if self.application:
                await self.application.bot.send_message(
                    chat_id=self.chat_id,
                    text=f"📅 Scan quotidien: {len(bullish_pairs)} BULLISH, {len(bearish_pairs)} BEARISH"
                )

        except Exception as e:
            logger.error(f"Erreur job_daily_scan: {e}")

    async def job_hourly_scan(self):
        """Job: Scan H1 horaire"""
        try:
            if not self.aligned_pairs:
                logger.debug("Aucune paire alignée à scanner")
                return

            logger.info(f"🔄 Démarrage du scan H1 pour {len(self.aligned_pairs)} paires...")

            for symbol, trend in self.aligned_pairs.items():
                try:
                    signal = self.scanner.scan_hourly_for_signals(symbol, trend)

                    if signal:
                        logger.info(f"✅ Signal détecté: {symbol} {trend}")

                        # Sauvegarder le signal
                        self.db.save_signal(
                            symbol=symbol,
                            timeframe="1h",
                            signal_type=signal.get("signal_type", ""),
                            price=signal.get("price", 0),
                            fib_level=signal.get("fib_zone", ""),
                            heiken_ashi_confirmed=True,
                            rsi_divergence=signal.get("rsi_divergence", False),
                            sr_confluence=signal.get("sr_confluence", False),
                        )

                        # Envoyer la notification
                        if self.application:
                            await self.application.bot.send_message(
                                chat_id=self.chat_id,
                                text=f"🚀 Signal: {symbol} {signal.get('signal_type', '')} @ {signal.get('price', 0):.5f}"
                            )

                except Exception as e:
                    logger.error(f"Erreur scan H1 {symbol}: {e}")

        except Exception as e:
            logger.error(f"Erreur job_hourly_scan: {e}")

    async def job_heartbeat(self):
        """Job: Heartbeat"""
        try:
            logger.info("💓 Heartbeat")
            if self.application:
                await self.application.bot.send_message(
                    chat_id=self.chat_id,
                    text="🤖 Bot actif"
                )

        except Exception as e:
            logger.error(f"Erreur job_heartbeat: {e}")

    def start(self):
        """Démarrer le scheduler"""
        try:
            self.scheduler.start()
            logger.info("Scheduler démarré")
        except Exception as e:
            logger.error(f"Erreur démarrage scheduler: {e}")

    def stop(self):
        """Arrêter le scheduler"""
        try:
            self.scheduler.shutdown()
            logger.info("Scheduler arrêté")
        except Exception as e:
            logger.error(f"Erreur arrêt scheduler: {e}")
