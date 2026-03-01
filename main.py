#!/usr/bin/env python3
import asyncio
import signal
import sys
import os
from threading import Thread
from flask import Flask
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram import Update
from config.secrets import Secrets
from config.settings import PAIRS
from data.twelvedata_client import TwelveDataClient
from data.database import Database
from bot.handlers import CommandHandlers
from scheduler.jobs import SchedulerManager
from utils.logger import setup_logger

logger = setup_logger(__name__)

flask_app = Flask(__name__)

@flask_app.route('/')
def health_check():
    return {'status': 'ok', 'bot': 'running'}, 200

@flask_app.route('/health')
def health():
    return {'status': 'healthy'}, 200

class FiboBotApp:
    def __init__(self):
        self.application = None
        self.running = True
        self.flask_thread = None
        self.scheduler_manager = None

    async def start(self):
        try:
            logger.info("🚀 Démarrage du bot Fibonacci...")
            
            # Charger les secrets
            token = Secrets.get_telegram_token()
            logger.info("✅ Secrets chargés")
            
            # Initialiser les clients
            self.api_client = TwelveDataClient()
            self.db = Database()
            logger.info("✅ Clients initialisés")
            
            # Créer l'application Telegram
            self.application = Application.builder().token(token).build()
            logger.info("✅ Application Telegram créée")
            
            # Ajouter les handlers
            handlers = CommandHandlers(self.api_client, self.db)
            self.application.add_handler(CommandHandler("start", handlers.start))
            self.application.add_handler(CommandHandler("status", handlers.status))
            self.application.add_handler(CommandHandler("pairs", handlers.pairs))
            self.application.add_handler(CommandHandler("history", handlers.history))
            self.application.add_handler(CommandHandler("stats", handlers.stats))
            logger.info("✅ Handlers configurés")
            
            # Démarrer le scheduler
            self.scheduler_manager = SchedulerManager(self.application, self.api_client, self.db)
            self.scheduler_manager.start()
            logger.info("✅ Scheduler démarré")
            
            # Démarrer Flask en arrière-plan
            self.flask_thread = Thread(target=lambda: flask_app.run(host='0.0.0.0', port=10000, debug=False), daemon=True)
            self.flask_thread.start()
            logger.info("✅ Serveur Flask démarré (port 10000)")
            
            # Démarrer le bot
            logger.info("✅ Application Telegram démarrée - En attente de messages...")
            await self.application.run_polling()
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation: {e}", exc_info=True)
            sys.exit(1)

    async def stop(self):
        try:
            logger.info("🛑 Arrêt du bot...")
            self.running = False
            if self.scheduler_manager:
                self.scheduler_manager.stop()
            logger.info("✅ Bot arrêté")
        except Exception as e:
            logger.error(f"❌ Erreur arrêt: {e}", exc_info=True)

async def main():
    app = FiboBotApp()
    
    def signal_handler(sig, frame):
        logger.info("Signal reçu, arrêt du bot...")
        asyncio.create_task(app.stop())
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    await app.start()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot arrêté par l'utilisateur")
    except Exception as e:
        logger.error(f"Erreur fatale: {e}", exc_info=True)
        sys.exit(1)
