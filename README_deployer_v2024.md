# 🚀 Bot de Prédiction Telegram - Déploiement Render.com v2024

## 📦 Contenu du Package
- **deployer_v2024_render_main.py** : Fichier principal optimisé Render
- **deployer_v2024_render.yaml** : Configuration service Render  
- **deployer_v2024_render_requirements.txt** : Dépendances Python
- **predictor.py** : Moteur de prédiction avec logique des As
- **yaml_manager.py** : Gestionnaire de données YAML
- **scheduler.py** : Planificateur automatique

## 🎯 Fonctionnalités v2024
✅ **Logique des As corrigée** : Lance prédiction SEULEMENT si As dans premier groupe uniquement  
✅ **Messages en temps réel** : Édition des prédictions sur place  
✅ **Vérification par offsets** : ✅0️⃣, ✅1️⃣, ✅2️⃣, ❌  
✅ **Planification automatique** : Timing variable 1-4 minutes  
✅ **Format unifié** : "🔵{numéro} 🔵3D: statut :⏳"  

## 🛠️ Instructions de Déploiement
1. Créer nouveau service Web sur Render.com
2. Connecter votre repository Git
3. Configurer: Build = pip install -r deployer_v2024_render_requirements.txt  
4. Start = python deployer_v2024_render_main.py
5. Ajouter variables d'environnement (voir .env.example)
6. Déployer et monitorer logs

## ⚙️ Variables Requises
- **API_ID** : ID application Telegram
- **API_HASH** : Hash application Telegram  
- **BOT_TOKEN** : Token bot Telegram
- **ADMIN_ID** : ID administrateur Telegram
- **PORT** : 10000 (auto-configuré par Render)

## 🎮 Règles de Prédiction
- Lance prédiction SI : 1 As dans premier groupe ET 0 dans deuxième
- Ne lance PAS SI : 2+ As dans premier groupe  
- Ne lance PAS SI : As dans deuxième groupe
- Ne lance PAS SI : As dans les deux groupes

Exemple : `#N1044. 2(A♠️A♥️10♥️) - ✅6(10♦️Q♥️6♠️)` → PAS de prédiction (2 As premier groupe)

## 🔧 Monitoring et Debug
- Health check disponible sur : `https://votre-app.onrender.com/health`
- Logs en temps réel dans dashboard Render.com
- Format de prédiction : "🔵{numéro} 🔵2D: {statut} :⏳"

## 📱 Commandes Bot (pour Admin)
- `/status` : Statut du bot
- `/reset` : Réinitialiser données
- `/ni` : Informations système

## 🚨 Troubleshooting
- Vérifier toutes les variables d'environnement sont configurées
- S'assurer que les channels sont correctement configurés
- Monitorer les logs pour détecter les erreurs de connexion
- Tester le health check endpoint régulièrement