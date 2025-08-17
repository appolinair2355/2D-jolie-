#!/usr/bin/env python3
"""
Bot de Prédiction Telegram v2024 - Version Complète pour Render.com
Architecture 100% YAML - Aucune base de données PostgreSQL requise
Logique des As optimisée : 1 As premier groupe + 0 As deuxième groupe
"""

import os
import asyncio
import re
import logging
import sys
import json
import zipfile
from datetime import datetime, timedelta
from telethon import TelegramClient, events
from predictor import CardPredictor  
from yaml_manager import YAMLManager, init_database
from scheduler import PredictionScheduler
from aiohttp import web
import time

# Configuration des logs optimisée pour Render.com
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Variables d'environnement
API_ID = int(os.getenv('API_ID', '0'))
API_HASH = os.getenv('API_HASH', '')
BOT_TOKEN = os.getenv('BOT_TOKEN', '')
ADMIN_ID = int(os.getenv('ADMIN_ID', '0'))
PORT = int(os.getenv('PORT', '10000'))
prediction_interval = int(os.getenv('PREDICTION_INTERVAL', '1'))

# Fichier de configuration
CONFIG_FILE = "bot_config.json"

# Variables d'état globales
detected_stat_channel = None
detected_display_channel = None
predictor = CardPredictor()
scheduler = None
yaml_manager = None

# Client Telegram
session_name = f'bot_session_{int(time.time())}'
client = TelegramClient(session_name, API_ID, API_HASH)

def load_config():
    """Charge la configuration depuis le fichier JSON"""
    global detected_stat_channel, detected_display_channel, prediction_interval
    
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                detected_stat_channel = config.get('stat_channel')
                detected_display_channel = config.get('display_channel')
                prediction_interval = config.get('prediction_interval', 1)
                logger.info(f"✅ Configuration chargée: Stats={detected_stat_channel}, Display={detected_display_channel}, Intervalle={prediction_interval}min")
                return True
    except Exception as e:
        logger.error(f"Erreur chargement config: {e}")
    
    return False

def save_config():
    """Sauvegarde la configuration dans le fichier JSON"""
    try:
        config = {
            'stat_channel': detected_stat_channel,
            'display_channel': detected_display_channel,
            'prediction_interval': prediction_interval
        }
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        logger.info("✅ Configuration sauvegardée")
        return True
    except Exception as e:
        logger.error(f"Erreur sauvegarde config: {e}")
        return False

# Health check pour Render.com
async def health_check(request):
    """Health check endpoint pour Render.com"""
    return web.Response(text=f"✅ Bot Telegram Prédiction v2024 - Port {PORT} - Running OK!", status=200)

async def bot_status_endpoint(request):
    """Endpoint de statut détaillé"""
    try:
        status = {
            "bot_online": True,
            "port": PORT,
            "stat_channel": detected_stat_channel,
            "display_channel": detected_display_channel,
            "prediction_interval": prediction_interval,
            "predictions_active": len(predictor.prediction_status),
            "scheduler_running": scheduler.is_running if scheduler else False,
            "yaml_database": "active",
            "timestamp": datetime.now().isoformat()
        }
        return web.json_response(status)
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

# --- COMMANDES TELEGRAM ---

@client.on(events.NewMessage(pattern='/start'))
async def start_command(event):
    """Commande de démarrage"""
    welcome_msg = f"""🎯 **Bot de Prédiction v2024 - Bienvenue !**

🔹 **Architecture YAML Pure** - Plus de PostgreSQL
🔹 **Logique As Optimisée** - 1 As premier + 0 As deuxième groupe
🔹 **Port {PORT}** - Configuré pour Render.com

**Fonctionnalités** :
• Prédictions automatiques avec logique des As
• Vérification des résultats avec statuts détaillés
• Configuration flexible de l'intervalle de prédiction
• Architecture YAML complète et autonome

**Commandes Administrateur** :
• `/status` - État complet du système
• `/intervalle [1-60]` - Configurer délai prédiction
• `/deploy` - Générer package de déploiement

Le bot est prêt ! 🚀"""
    
    await event.respond(welcome_msg)
    logger.info(f"Message bienvenue envoyé à {event.sender_id}")

@client.on(events.NewMessage(pattern='/status'))
async def status_command(event):
    """Affiche le statut complet du système"""
    if event.sender_id != ADMIN_ID:
        return
    
    try:
        # Statistiques du scheduler
        if scheduler:
            sched_stats = scheduler.get_statistics()
            sched_status = f"""📊 **Planificateur**:
• État: {'🟢 Actif' if sched_stats['is_running'] else '🔴 Inactif'}
• Total planifié: {sched_stats['total_scheduled']}
• Lancées: {sched_stats['launched']}
• Vérifiées: {sched_stats['verified']}
• En attente: {sched_stats['pending']}
• Taux réussite: {sched_stats['success_rate']:.1f}%"""
        else:
            sched_status = "📊 **Planificateur**: Non initialisé"
        
        # Statistiques du prédicteur
        pred_stats = predictor.get_statistics()
        pred_status = f"""🎯 **Prédicteur**:
• Total prédictions: {pred_stats['total']}
• Réussites: {pred_stats['wins']} ✅
• Échecs: {pred_stats['losses']} ❌
• En attente: {pred_stats['pending']} ⏳
• Taux réussite: {pred_stats['win_rate']:.1f}%"""
        
        status_msg = f"""📊 **État du Bot v2024**

🌐 **Configuration**:
• Canal statistiques: {'✅' if detected_stat_channel else '❌'} ({detected_stat_channel})
• Canal affichage: {'✅' if detected_display_channel else '❌'} ({detected_display_channel})
• Port serveur: {PORT}
• Intervalle prédiction: {prediction_interval} minute(s)

{sched_status}

{pred_status}

🔧 **Architecture**:
• Base données: YAML (autonome)
• Logique As: 1 premier + 0 deuxième groupe
• Version: v2024 Render.com"""
        
        await event.respond(status_msg)
        
    except Exception as e:
        logger.error(f"Erreur status: {e}")
        await event.respond(f"❌ Erreur: {e}")

@client.on(events.NewMessage(pattern=r'/intervalle (\d+)'))
async def set_prediction_interval(event):
    """Configure l'intervalle de prédiction"""
    if event.sender_id != ADMIN_ID:
        return
        
    try:
        global prediction_interval
        new_interval = int(event.pattern_match.group(1))
        
        if 1 <= new_interval <= 60:
            old_interval = prediction_interval
            prediction_interval = new_interval
            
            # Sauvegarder la configuration
            save_config()
            
            await event.respond(f"""✅ **Intervalle de Prédiction Mis à Jour**

⏱️ **Ancien**: {old_interval} minute(s)
⏱️ **Nouveau**: {prediction_interval} minute(s)

Le système utilisera maintenant ce nouvel intervalle pour espacer les prédictions automatiques.

Configuration sauvegardée automatiquement.""")
            
            logger.info(f"✅ Intervalle mis à jour: {old_interval} → {prediction_interval} minutes")
        else:
            await event.respond("❌ **Erreur**: L'intervalle doit être entre 1 et 60 minutes")
            
    except ValueError:
        await event.respond("❌ **Erreur**: Veuillez entrer un nombre valide")
    except Exception as e:
        logger.error(f"Erreur set_prediction_interval: {e}")
        await event.respond(f"❌ Erreur: {e}")

# Messages handler principal avec logique As
@client.on(events.NewMessage())
@client.on(events.MessageEdited())
async def handle_messages(event):
    """Gestionnaire principal des messages"""
    try:
        message_text = event.message.message if event.message else ""
        channel_id = event.chat_id
        
        # Vérifier si c'est le bon canal
        if detected_stat_channel and channel_id == detected_stat_channel:
            logger.info(f"✅ Message du canal stats: {message_text[:100]}")
            
            # Logique de prédiction avec analyse des As
            should_predict, game_number, suit = predictor.should_predict(message_text)
            if should_predict and game_number and suit:
                prediction_text = f"🔵{game_number} 🔵3D: {suit} :⏳"
                logger.info(f"🎯 Prédiction générée: {prediction_text}")
                
                # Diffuser la prédiction si canal configuré
                if detected_display_channel:
                    try:
                        await client.send_message(detected_display_channel, prediction_text)
                        logger.info(f"📤 Prédiction diffusée sur canal {detected_display_channel}")
                    except Exception as e:
                        logger.error(f"Erreur diffusion: {e}")
            
            # Vérification des résultats
            verified, number = predictor.verify_prediction(message_text)
            if verified is not None and number is not None:
                status = predictor.prediction_status.get(number, '❌')
                logger.info(f"🔍 Vérification jeu #{number}: {status}")
                
        else:
            logger.debug(f"Message ignoré - Canal {channel_id} ≠ Stats {detected_stat_channel}")
            
    except Exception as e:
        logger.error(f"Erreur handle_messages: {e}")

# Démarrage serveur web
async def start_web_server():
    """Démarre le serveur web pour Render.com"""
    app = web.Application()
    app.router.add_get('/', health_check)
    app.router.add_get('/health', health_check)
    app.router.add_get('/status', bot_status_endpoint)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    logger.info(f"✅ Serveur web démarré sur 0.0.0.0:{PORT}")

async def main():
    """Fonction principale"""
    try:
        logger.info("🚀 Démarrage Bot Prédiction v2024")
        
        # Vérifier les variables d'environnement
        if not API_ID or not API_HASH or not BOT_TOKEN or not ADMIN_ID:
            logger.error("❌ Variables d'environnement manquantes!")
            return
            
        logger.info(f"✅ Configuration: API_ID={API_ID}, ADMIN_ID={ADMIN_ID}, PORT={PORT}")
        
        # Initialiser YAML
        global yaml_manager
        yaml_manager = YAMLManager()
        init_database()
        logger.info("✅ Gestionnaire YAML initialisé")
        
        # Charger configuration
        load_config()
        
        # Démarrer serveur web
        await start_web_server()
        
        # Démarrer bot Telegram
        logger.info("🔗 Connexion au bot Telegram...")
        await client.start(bot_token=BOT_TOKEN)
        
        me = await client.get_me()
        logger.info(f"✅ Bot connecté: @{me.username}")
        logger.info("🔄 Bot en ligne et en attente de messages...")
        logger.info(f"🌐 Accès web: http://0.0.0.0:{PORT}")
        
        # Boucle principale
        await client.run_until_disconnected()
        
    except Exception as e:
        logger.error(f"❌ Erreur critique: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())