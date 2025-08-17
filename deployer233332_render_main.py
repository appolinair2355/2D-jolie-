#!/usr/bin/env python3
"""
🚀 Telegram Card Prediction Bot - Version Render.com Optimisée
📦 Package: deployer233332
📊 Logs détaillés pour surveillance Render.com
"""

import asyncio
import logging
import sys
import os
from aiohttp import web
from telethon import TelegramClient, events
from telethon.tl.types import Channel, Chat
from datetime import datetime, timedelta
import json
import yaml
import traceback

# Configuration du logging pour Render.com
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('render_bot.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Import des modules locaux
try:
    from deployer233332_render_predictor import CardPredictor
    try:
        from deployer233332_yaml_manager import YAMLDataManager
    except ImportError:
        # Fallback si yaml_manager n'est pas trouvé
        logger.warning("⚠️ yaml_manager non trouvé, utilisation du système simplifié")
        class YAMLDataManager:
            def __init__(self):
                self.data = {}
            def get_config(self, key): return None
            def set_config(self, key, value): pass
            def save_prediction(self, data): pass
except ImportError as e:
    logger.error(f"❌ Erreur import critique: {e}")
    sys.exit(1)

class TelegramBot:
    def __init__(self):
        self.api_id = int(os.getenv('API_ID', 0))
        self.api_hash = os.getenv('API_HASH', '')
        self.bot_token = os.getenv('BOT_TOKEN', '')
        self.admin_id = int(os.getenv('ADMIN_ID', 0))
        self.port = int(os.getenv('PORT', 10000))
        
        logger.info(f"🔧 Configuration: API_ID={self.api_id}, ADMIN_ID={self.admin_id}, PORT={self.port}")
        
        if not all([self.api_id, self.api_hash, self.bot_token, self.admin_id]):
            logger.error("❌ Configuration manquante - Vérifiez les variables d'environnement")
            raise ValueError("Configuration incomplète")
        
        # Initialisation des composants
        self.predictor = CardPredictor()
        self.database = YAMLDataManager()
        
        # Configuration bot
        self.client = TelegramClient('render_bot_session', self.api_id, self.api_hash)
        self.stats_channel_id = None
        self.display_channel_id = None
        self.prediction_interval = 1  # minutes
        
        logger.info("✅ Composants initialisés")

    async def start_bot(self):
        """Démarrage du bot Telegram"""
        try:
            await self.client.start(bot_token=self.bot_token)
            me = await self.client.get_me()
            username = getattr(me, 'username', 'Unknown')
            logger.info(f"✅ Bot connecté: @{username}")
            
            # Chargement configuration
            await self.load_configuration()
            
            # Enregistrement des handlers
            self.register_handlers()
            
            logger.info("🚀 Bot prêt - En attente de messages...")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur démarrage bot: {e}")
            logger.error(traceback.format_exc())
            return False

    async def load_configuration(self):
        """Chargement de la configuration depuis YAML"""
        try:
            config = await self.database.get_config()
            if config:
                self.stats_channel_id = config.get('stats_channel')
                self.display_channel_id = config.get('display_channel')
                self.prediction_interval = config.get('prediction_interval', 1)
                logger.info(f"✅ Configuration chargée: Stats={self.stats_channel_id}, Display={self.display_channel_id}, Intervalle={self.prediction_interval}min")
            else:
                logger.info("ℹ️ Configuration par défaut utilisée")
        except Exception as e:
            logger.error(f"❌ Erreur chargement configuration: {e}")

    def register_handlers(self):
        """Enregistrement des handlers d'événements"""
        
        @self.client.on(events.NewMessage())
        async def handle_new_message(event):
            try:
                await self.process_message(event)
            except Exception as e:
                logger.error(f"❌ Erreur traitement message: {e}")
                logger.error(traceback.format_exc())
        
        @self.client.on(events.MessageEdited())
        async def handle_edited_message(event):
            try:
                await self.process_edited_message(event)
            except Exception as e:
                logger.error(f"❌ Erreur traitement édition: {e}")
                logger.error(traceback.format_exc())

        logger.info("✅ Handlers enregistrés")

    async def process_message(self, event):
        """Traitement des nouveaux messages"""
        try:
            message = event.message
            chat_id = message.peer_id.channel_id if hasattr(message.peer_id, 'channel_id') else None
            
            logger.info(f"📬 NOUVEAU MESSAGE: Canal {chat_id} | Texte: {message.text[:100]}...")
            
            # Vérification canal stats
            if self.stats_channel_id and chat_id != self.stats_channel_id:
                logger.debug(f"🔧 Message ignoré - Canal {chat_id} ≠ Canal stats {self.stats_channel_id}")
                return
            
            if not message.text:
                return
                
            logger.info(f"✅ Message accepté pour traitement: {message.text[:50]}...")
            
            # Traitement prédiction
            should_predict, predicted_game, predicted_cards = self.predictor.should_predict(message.text)
            
            if should_predict and predicted_game and predicted_cards and self.display_channel_id:
                await self.send_prediction(predicted_game, predicted_cards)
                logger.info(f"🎯 Prédiction envoyée: Jeu #{predicted_game} -> {predicted_cards}")
            
            # Vérification des résultats
            await self.check_and_update_predictions(message.text)
            
        except Exception as e:
            logger.error(f"❌ Erreur process_message: {e}")
            logger.error(traceback.format_exc())

    async def process_edited_message(self, event):
        """Traitement des messages édités"""
        try:
            message = event.message
            chat_id = message.peer_id.channel_id if hasattr(message.peer_id, 'channel_id') else None
            
            logger.info(f"✏️ MESSAGE ÉDITÉ: Canal {chat_id} | Texte: {message.text[:100]}...")
            
            if self.stats_channel_id and chat_id != self.stats_channel_id:
                logger.debug(f"🔧 Édition ignorée - Canal {chat_id} ≠ Canal stats {self.stats_channel_id}")
                return
            
            if message.text and ('🔰' in message.text or '✅' in message.text):
                logger.info(f"🔄 Message finalisé détecté: {message.text[:50]}...")
                await self.check_and_update_predictions(message.text)
            
        except Exception as e:
            logger.error(f"❌ Erreur process_edited_message: {e}")
            logger.error(traceback.format_exc())

    async def send_prediction(self, game_number: int, predicted_cards: str):
        """Envoi d'une prédiction au canal display"""
        try:
            # Format uniforme: 🔵XXX 🔵2D: statut :⏳
            prediction_text = f"🔵{game_number} 🔵2D: statut :⏳"
            
            # Envoi au canal display
            if self.display_channel_id:
                sent_message = await self.client.send_message(
                    self.display_channel_id, 
                    prediction_text
                )
                
                # Sauvegarde du message pour édition ultérieure  
                await self.database.save_prediction(game_number, predicted_cards, sent_message.id)
            else:
                logger.warning("❌ Canal display non configuré")
            
            logger.info(f"✅ Prédiction envoyée: {prediction_text}")
            
        except Exception as e:
            logger.error(f"❌ Erreur envoi prédiction: {e}")
            logger.error(traceback.format_exc())

    async def check_and_update_predictions(self, message_text: str):
        """Vérification et mise à jour des prédictions"""
        try:
            game_number = self.predictor.extract_game_number(message_text)
            if not game_number:
                return
            
            logger.info(f"🔍 Vérification résultat pour jeu #{game_number}")
            
            # Récupération prédictions en attente
            predictions = await self.database.get_pending_predictions()
            
            for pred in predictions:
                pred_game = pred.get('game_number')
                pred_cards = pred.get('predicted_cards')
                msg_id = pred.get('message_id')
                
                if not pred_game or pred_game > game_number + 3:
                    continue
                
                # Vérification avec offset étendu (prédit+0 à prédit+3)
                if game_number == pred_game + 3:  # Logique simplifiée prédit+3
                    status = self.predictor.verify_prediction_offset_3(message_text, pred_cards)
                    
                    if status and msg_id:
                        # Mise à jour du message
                        new_text = f"🔵{pred_game} 🔵2D: statut :{status}"
                        await self.update_prediction_message(msg_id, new_text)
                        
                        # Mise à jour base de données
                        await self.database.update_prediction_status(pred_game, status)
                        
                        logger.info(f"✅ Prédiction #{pred_game} mise à jour: {status}")
            
        except Exception as e:
            logger.error(f"❌ Erreur vérification prédictions: {e}")
            logger.error(traceback.format_exc())

    async def update_prediction_message(self, message_id: int, new_text: str):
        """Mise à jour d'un message de prédiction"""
        try:
            if self.display_channel_id:
                await self.client.edit_message(
                    self.display_channel_id,
                    message_id,
                    new_text
                )
            logger.info(f"✅ Message {message_id} mis à jour: {new_text}")
            
        except Exception as e:
            logger.error(f"❌ Erreur mise à jour message {message_id}: {e}")

    async def start_web_server(self):
        """Démarrage serveur web pour health check Render"""
        app = web.Application()
        
        async def health_check(request):
            """Endpoint de santé pour Render.com"""
            status = {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'bot_running': self.client.is_connected(),
                'version': 'deployer233332',
                'stats_channel': self.stats_channel_id,
                'display_channel': self.display_channel_id
            }
            logger.info(f"🏥 Health check: {status}")
            return web.json_response(status)
        
        async def root_handler(request):
            """Page d'accueil"""
            return web.json_response({
                'message': 'Telegram Card Prediction Bot - deployer233332',
                'status': 'running',
                'logs': 'Check /health for detailed status'
            })
        
        app.router.add_get('/', root_handler)
        app.router.add_get('/health', health_check)
        
        # Démarrage serveur
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', self.port)
        await site.start()
        
        logger.info(f"🌐 Serveur web démarré sur port {self.port}")
        logger.info(f"🔗 Health check: http://0.0.0.0:{self.port}/health")

async def main():
    """Fonction principale"""
    try:
        logger.info("🚀 DÉMARRAGE BOT TELEGRAM - deployer233332")
        logger.info("=" * 50)
        
        # Initialisation bot
        bot = TelegramBot()
        
        # Démarrage serveur web
        await bot.start_web_server()
        
        # Démarrage bot Telegram
        if await bot.start_bot():
            logger.info("✅ TOUS SYSTÈMES OPÉRATIONNELS")
            logger.info("🎯 Bot en attente de messages...")
            logger.info("📊 Logs détaillés activés pour Render.com")
            
            # Boucle infinie
            if bot.client:
                await bot.client.run_until_disconnected()
        else:
            logger.error("❌ ÉCHEC DÉMARRAGE BOT")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("⏹️ Arrêt bot par utilisateur")
    except Exception as e:
        logger.error(f"💥 ERREUR CRITIQUE: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())