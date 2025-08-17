#!/usr/bin/env python3
"""
📁 YAML Data Manager - Version deployer233332
💾 Gestionnaire de données YAML optimisé avec logging détaillé
"""

import os
import yaml
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class YAMLDataManager:
    """Gestionnaire de données basé sur YAML"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.ensure_data_directory()
        
        # Fichiers de données
        self.files = {
            'config': os.path.join(data_dir, 'bot_config.yaml'),
            'predictions': os.path.join(data_dir, 'predictions.yaml'),
            'auto_predictions': os.path.join(data_dir, 'auto_predictions.yaml'),
            'message_log': os.path.join(data_dir, 'message_log.yaml')
        }
        
        logger.info(f"✅ YAMLDataManager initialisé: répertoire {data_dir}")
    
    def ensure_data_directory(self):
        """Création du répertoire data si nécessaire"""
        try:
            if not os.path.exists(self.data_dir):
                os.makedirs(self.data_dir)
                logger.info(f"📁 Répertoire créé: {self.data_dir}")
        except Exception as e:
            logger.error(f"❌ Erreur création répertoire: {e}")
    
    def load_yaml_file(self, filepath: str, default: Any = None) -> Any:
        """Chargement fichier YAML avec gestion d'erreurs"""
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f) or default
                    logger.debug(f"📖 Chargé: {filepath}")
                    return data
            else:
                logger.debug(f"📄 Fichier inexistant, utilisation défaut: {filepath}")
                return default or {}
        except Exception as e:
            logger.error(f"❌ Erreur lecture {filepath}: {e}")
            return default or {}
    
    def save_yaml_file(self, filepath: str, data: Any):
        """Sauvegarde fichier YAML avec gestion d'erreurs"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
            logger.debug(f"💾 Sauvegardé: {filepath}")
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde {filepath}: {e}")
    
    # Configuration du bot
    async def get_config(self) -> Dict:
        """Récupération configuration bot"""
        try:
            config = self.load_yaml_file(self.files['config'], {
                'stats_channel': None,
                'display_channel': None,
                'prediction_interval': 1,
                'last_updated': datetime.now().isoformat()
            })
            logger.info(f"⚙️ Configuration chargée: {config}")
            return config
        except Exception as e:
            logger.error(f"❌ Erreur get_config: {e}")
            return {}
    
    async def save_config(self, config: Dict):
        """Sauvegarde configuration bot"""
        try:
            config['last_updated'] = datetime.now().isoformat()
            self.save_yaml_file(self.files['config'], config)
            logger.info(f"✅ Configuration sauvegardée: {config}")
        except Exception as e:
            logger.error(f"❌ Erreur save_config: {e}")
    
    # Gestion des prédictions
    async def save_prediction(self, game_number: int, predicted_cards: str, message_id: int):
        """Sauvegarde d'une prédiction"""
        try:
            predictions = self.load_yaml_file(self.files['predictions'], {})
            
            prediction_data = {
                'game_number': game_number,
                'predicted_cards': predicted_cards,
                'message_id': message_id,
                'status': 'pending',
                'created_at': datetime.now().isoformat()
            }
            
            predictions[str(game_number)] = prediction_data
            self.save_yaml_file(self.files['predictions'], predictions)
            
            logger.info(f"💾 Prédiction sauvegardée: #{game_number} -> {predicted_cards}")
        except Exception as e:
            logger.error(f"❌ Erreur save_prediction: {e}")
    
    async def get_pending_predictions(self) -> List[Dict]:
        """Récupération prédictions en attente"""
        try:
            predictions = self.load_yaml_file(self.files['predictions'], {})
            pending = [
                pred for pred in predictions.values() 
                if pred.get('status') == 'pending'
            ]
            logger.debug(f"🔍 Prédictions en attente: {len(pending)}")
            return pending
        except Exception as e:
            logger.error(f"❌ Erreur get_pending_predictions: {e}")
            return []
    
    async def update_prediction_status(self, game_number: int, status: str):
        """Mise à jour statut prédiction"""
        try:
            predictions = self.load_yaml_file(self.files['predictions'], {})
            
            if str(game_number) in predictions:
                predictions[str(game_number)]['status'] = status
                predictions[str(game_number)]['updated_at'] = datetime.now().isoformat()
                
                self.save_yaml_file(self.files['predictions'], predictions)
                logger.info(f"✅ Statut mis à jour: #{game_number} -> {status}")
            else:
                logger.warning(f"⚠️ Prédiction #{game_number} non trouvée")
        except Exception as e:
            logger.error(f"❌ Erreur update_prediction_status: {e}")
    
    # Gestion des prédictions automatiques
    async def save_auto_prediction(self, date_key: str, prediction_data: Dict):
        """Sauvegarde prédiction automatique"""
        try:
            auto_preds = self.load_yaml_file(self.files['auto_predictions'], {})
            
            if date_key not in auto_preds:
                auto_preds[date_key] = []
            
            auto_preds[date_key].append({
                **prediction_data,
                'created_at': datetime.now().isoformat()
            })
            
            self.save_yaml_file(self.files['auto_predictions'], auto_preds)
            logger.info(f"🤖 Prédiction auto sauvegardée: {date_key}")
        except Exception as e:
            logger.error(f"❌ Erreur save_auto_prediction: {e}")
    
    async def get_auto_predictions(self, date_key: str) -> List[Dict]:
        """Récupération prédictions automatiques d'une date"""
        try:
            auto_preds = self.load_yaml_file(self.files['auto_predictions'], {})
            predictions = auto_preds.get(date_key, [])
            logger.debug(f"🤖 Prédictions auto {date_key}: {len(predictions)}")
            return predictions
        except Exception as e:
            logger.error(f"❌ Erreur get_auto_predictions: {e}")
            return []
    
    # Log des messages
    async def log_message(self, message_data: Dict):
        """Log d'un message traité"""
        try:
            message_log = self.load_yaml_file(self.files['message_log'], [])
            
            log_entry = {
                **message_data,
                'timestamp': datetime.now().isoformat()
            }
            
            message_log.append(log_entry)
            
            # Nettoyage automatique (garder 1000 derniers)
            if len(message_log) > 1000:
                message_log = message_log[-1000:]
            
            self.save_yaml_file(self.files['message_log'], message_log)
            logger.debug("📝 Message loggé")
        except Exception as e:
            logger.error(f"❌ Erreur log_message: {e}")
    
    # Statistiques
    async def get_prediction_stats(self) -> Dict:
        """Statistiques des prédictions"""
        try:
            predictions = self.load_yaml_file(self.files['predictions'], {})
            
            total = len(predictions)
            if total == 0:
                return {'total': 0, 'success': 0, 'pending': 0, 'rate': 0.0}
            
            success = sum(1 for p in predictions.values() if '✅' in str(p.get('status', '')))
            pending = sum(1 for p in predictions.values() if p.get('status') == 'pending')
            rate = (success / total) * 100 if total > 0 else 0.0
            
            stats = {
                'total': total,
                'success': success,
                'pending': pending,
                'rate': round(rate, 1)
            }
            
            logger.info(f"📊 Stats calculées: {stats}")
            return stats
        except Exception as e:
            logger.error(f"❌ Erreur get_prediction_stats: {e}")
            return {'total': 0, 'success': 0, 'pending': 0, 'rate': 0.0}
    
    # Nettoyage
    async def cleanup_old_data(self, days: int = 30):
        """Nettoyage données anciennes"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Nettoyage prédictions
            predictions = self.load_yaml_file(self.files['predictions'], {})
            cleaned_predictions = {}
            
            for key, pred in predictions.items():
                created_at = pred.get('created_at')
                if created_at:
                    pred_date = datetime.fromisoformat(created_at.replace('Z', '+00:00').replace('+00:00', ''))
                    if pred_date > cutoff_date:
                        cleaned_predictions[key] = pred
            
            if len(cleaned_predictions) != len(predictions):
                self.save_yaml_file(self.files['predictions'], cleaned_predictions)
                logger.info(f"🧹 Nettoyage: {len(predictions) - len(cleaned_predictions)} prédictions supprimées")
            
        except Exception as e:
            logger.error(f"❌ Erreur cleanup_old_data: {e}")
    
    def __str__(self):
        return f"YAMLDataManager(dir={self.data_dir})"