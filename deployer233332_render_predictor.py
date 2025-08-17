#!/usr/bin/env python3
"""
🎯 Card Prediction Engine - Version deployer233332
📊 Moteur de prédiction optimisé avec logging détaillé
"""

import re
import random
import logging
from typing import Tuple, Optional, List

logger = logging.getLogger(__name__)

class CardPredictor:
    """Moteur de prédiction de cartes avec vérification des résultats"""
    
    def __init__(self):
        self.last_predictions = []
        self.prediction_status = {}
        self.processed_messages = set()
        self.status_log = []
        self.prediction_messages = {}
        self.pending_edit_messages = {}
        
        # Système déclencheurs - numéros 7, 8
        self.trigger_numbers = {7, 8}
        
        logger.info("✅ CardPredictor initialisé avec déclencheurs: 7, 8")
        
    def reset(self):
        """Réinitialisation des données de prédiction"""
        self.last_predictions.clear()
        self.prediction_status.clear()
        self.processed_messages.clear()
        self.status_log.clear()
        self.prediction_messages.clear()
        self.pending_edit_messages.clear()
        logger.info("🔄 Données prédiction réinitialisées")

    def extract_game_number(self, message: str) -> Optional[int]:
        """Extraction numéro de jeu depuis message"""
        try:
            # Pattern #N suivi de chiffres
            match = re.search(r"#N\s*(\d+)\.?", message, re.IGNORECASE)
            if match:
                number = int(match.group(1))
                logger.debug(f"🔢 Numéro extrait: {number}")
                return number
            
            # Pattern alternatif
            match = re.search(r"jeu\s*#?\s*(\d+)", message, re.IGNORECASE)
            if match:
                number = int(match.group(1))
                logger.debug(f"🔢 Numéro alternatif extrait: {number}")
                return number
                
            return None
            
        except (ValueError, AttributeError) as e:
            logger.error(f"❌ Erreur extraction numéro: {e}")
            return None

    def extract_symbols_from_parentheses(self, message: str) -> List[str]:
        """Extraction symboles de cartes depuis parenthèses"""
        try:
            # Recherche groupes entre parenthèses
            matches = re.findall(r'\(([^)]+)\)', message)
            if matches:
                logger.debug(f"🃏 Groupes extraits: {matches}")
                return matches
            return []
            
        except Exception as e:
            logger.error(f"❌ Erreur extraction symboles: {e}")
            return []

    def count_card_symbols(self, text: str) -> int:
        """Comptage symboles de cartes (♠️, ♥️, ♦️, ♣️)"""
        card_symbols = ['♠️', '♥️', '♦️', '♣️', '♠', '♥', '♦', '♣']
        count = sum(text.count(symbol) for symbol in card_symbols)
        logger.debug(f"🎴 Symboles comptés: {count}")
        return count

    def normalize_suits(self, suits_str: str) -> str:
        """Normalisation et tri des couleurs de cartes"""
        # Mapping emoji vers versions simples
        suit_map = {
            '♠️': '♠', '♥️': '♥', '♦️': '♦', '♣️': '♣'
        }
        
        normalized = suits_str
        for emoji, simple in suit_map.items():
            normalized = normalized.replace(emoji, simple)
        
        # Extraction et tri symboles
        suits = [c for c in normalized if c in '♠♥♦♣']
        result = ''.join(sorted(set(suits)))
        logger.debug(f"🔤 Couleurs normalisées: {result}")
        return result

    def should_predict(self, message: str) -> Tuple[bool, Optional[int], Optional[str]]:
        """Détermine si une prédiction doit être faite"""
        try:
            # Extraction numéro de jeu
            game_number = self.extract_game_number(message)
            if game_number is None:
                return False, None, None

            logger.info(f"🎯 Analyse jeu #{game_number}")

            # Vérification si déjà traité
            if game_number in self.prediction_status:
                logger.debug(f"⏭️ Jeu #{game_number} déjà traité")
                return False, None, None

            # Vérification déclencheurs (7, 8)
            last_digit = game_number % 10
            if last_digit not in self.trigger_numbers:
                logger.debug(f"🚫 Jeu #{game_number} ne déclenche pas (chiffre {last_digit})")
                return False, None, None

            logger.info(f"✅ Jeu #{game_number} déclenche prédiction (chiffre {last_digit})")

            # Extraction symboles
            matches = self.extract_symbols_from_parentheses(message)
            if not matches:
                logger.debug("❌ Aucun symbole trouvé")
                return False, None, None

            # Premier groupe de symboles
            first_group = matches[0]
            suits = self.normalize_suits(first_group)
            
            if not suits:
                logger.debug("❌ Aucune couleur valide")
                return False, None, None

            # Vérification doublons
            message_hash = hash(message.strip())
            if message_hash in self.processed_messages:
                self.prediction_status[game_number] = 'déjà traité'
                logger.debug(f"🔄 Message #{game_number} déjà traité")
                return False, None, None

            # Marquer comme traité
            self.processed_messages.add(message_hash)
            
            # Prédiction pour prochain round
            predicted_game = ((game_number // 10) + 1) * 10
            
            self.prediction_status[predicted_game] = '⌛'
            self.last_predictions.append((predicted_game, suits))
            
            logger.info(f"🎯 PRÉDICTION CRÉÉE: Jeu #{predicted_game} -> {suits} (basé sur #{game_number})")
            return True, predicted_game, suits

        except Exception as e:
            logger.error(f"❌ Erreur should_predict: {e}")
            return False, None, None

    def verify_prediction_offset_3(self, message: str, predicted_cards: str) -> Optional[str]:
        """Vérification prédiction avec offset +3 uniquement"""
        try:
            logger.info(f"🔍 Vérification offset +3: {predicted_cards}")
            
            # Extraction groupes de symboles
            matches = self.extract_symbols_from_parentheses(message)
            if len(matches) < 2:
                logger.debug("❌ Pas assez de groupes pour vérification")
                return "❌❌"
            
            # Vérification 2+2 cartes
            first_group_count = self.count_card_symbols(matches[0])
            second_group_count = self.count_card_symbols(matches[1])
            
            if first_group_count != 2 or second_group_count != 2:
                logger.debug(f"❌ Format non valide: {first_group_count}+{second_group_count} cartes")
                return "❌❌"
            
            # Normalisation couleurs prédites
            predicted_suits = set(predicted_cards)
            
            # Vérification dans les deux groupes
            for i, group in enumerate(matches):
                group_suits = set(self.normalize_suits(group))
                
                if predicted_suits.issubset(group_suits):
                    logger.info(f"✅ Match trouvé groupe {i+1}: {group_suits} contient {predicted_suits}")
                    return "✅3️⃣"
            
            logger.info(f"❌ Aucun match: prédit {predicted_suits}, trouvé {[self.normalize_suits(g) for g in matches]}")
            return "❌❌"
            
        except Exception as e:
            logger.error(f"❌ Erreur vérification: {e}")
            return "❌❌"

    def get_prediction_stats(self) -> dict:
        """Statistiques des prédictions"""
        try:
            total = len(self.status_log)
            if total == 0:
                return {'total': 0, 'success': 0, 'rate': 0.0}
            
            success = sum(1 for status in self.status_log if '✅' in status)
            rate = (success / total) * 100
            
            stats = {
                'total': total,
                'success': success,
                'rate': round(rate, 1)
            }
            
            logger.info(f"📊 Statistiques: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"❌ Erreur calcul stats: {e}")
            return {'total': 0, 'success': 0, 'rate': 0.0}

    def generate_auto_prediction(self) -> Tuple[str, str]:
        """Génération prédiction automatique avec couleurs aléatoires"""
        try:
            # Couleurs disponibles
            suits = ['♠', '♥', '♦', '♣']
            
            # Sélection aléatoire 2 couleurs
            selected_suits = random.sample(suits, 2)
            
            # Format comme 2K/2K (couleurs aléatoires)
            prediction = f"2{selected_suits[0]}/2{selected_suits[1]}"
            
            logger.info(f"🎲 Prédiction auto générée: {prediction}")
            return prediction, ''.join(selected_suits)
            
        except Exception as e:
            logger.error(f"❌ Erreur génération auto: {e}")
            return "2♠/2♥", "♠♥"

    def __str__(self):
        return f"CardPredictor(predictions={len(self.last_predictions)}, processed={len(self.processed_messages)})"