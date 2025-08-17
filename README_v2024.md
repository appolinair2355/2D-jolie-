# Package Déploiement v2024 - Bot Prédiction Telegram

## Nouvelles Fonctionnalités v2024:
✅ **Migration PostgreSQL → YAML**: Architecture complètement autonome
✅ **Stockage fichiers locaux**: Dossier data/ avec fichiers YAML structurés  
✅ **Performance optimisée**: Plus de connexions base de données externes
✅ **Logique des As perfectionnée**: 1 As premier groupe ET 0 As deuxième groupe
✅ **Commande /intervalle**: Configuration délai prédiction 1-60 minutes
✅ **Format unifié**: Messages "🔵{numéro} 🔵3D: statut :⏳"

## Architecture YAML Complete:
- bot_config.yaml: Configuration persistante
- predictions.yaml: Historique prédictions  
- auto_predictions.yaml: Planification automatique
- message_log.yaml: Logs avec nettoyage automatique

## Configuration Render.com:
- Port: 10000 (configuré automatiquement)
- Start Command: python deployer_v2024_complete_main.py  
- Build Command: pip install -r deployer_v2024_render_requirements.txt
- Variables: API_ID, API_HASH, BOT_TOKEN, ADMIN_ID
- AUCUNE base de données PostgreSQL requise

## Commandes Bot Disponibles:
/intervalle [1-60] - Configurer délai prédiction (défaut: 1min)
/status - État complet du système
/deploy - Générer package déploiement

## Règles Prédiction As:
- Lancer prédiction UNIQUEMENT si: 1 As premier groupe + 0 As deuxième groupe
- Exemples VALIDES: (A♠️K♥️) - (Q♦️J♣️) ✅
- Exemples INVALIDES: (A♠️A♥️K♦️) ou (K♥️Q♦️) - (A♠️J♣️) ❌

🚀 Package v2024 - 100% YAML avec logique As optimisée!