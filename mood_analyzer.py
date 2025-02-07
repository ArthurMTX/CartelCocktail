import numpy as np
from typing import List, Tuple, Dict, Any
import logging

class MoodAnalyzer:
    def __init__(self):
        self.base_characteristics = {
            "pop": [0.8, 0.8, 0.6, 0.5, 0.6],
            "rap": [0.8, 0.7, 0.6, 0.7, 0.6],
            "rock": [0.8, 0.5, 0.7, 0.8, 0.7],
            "electronic": [0.9, 0.9, 0.4, 0.6, 0.7],
            "classical": [0.4, 0.2, 0.9, 0.6, 1.0],
            "jazz": [0.5, 0.5, 0.8, 0.5, 0.9],
            "metal": [0.9, 0.4, 0.7, 1.0, 0.7],
            "indie": [0.6, 0.5, 0.8, 0.5, 0.8],
            "soul": [0.6, 0.6, 0.9, 0.5, 0.8],
            "folk": [0.4, 0.3, 0.8, 0.4, 0.7],
            "ambient": [0.3, 0.2, 0.7, 0.3, 0.8],
            "latin": [0.8, 0.9, 0.7, 0.6, 0.6],
            "blues": [0.5, 0.4, 0.9, 0.6, 0.8]
        }

        self.genre_modifiers = {
            "alternative": [0.0, -0.1, 0.1, 0.1, 0.1],   # More emotional and intense
            "dance": [0.1, 0.3, -0.1, 0.0, -0.1],       # More danceable
            "trap": [0.1, 0.1, -0.2, 0.2, -0.1],        # More intense, less emotional
            "hardcore": [0.2, 0.0, 0.0, 0.3, 0.0],      # More energetic and intense
            "progressive": [0.0, -0.1, 0.1, 0.1, 0.2],  # More sophisticated
            "psychedelic": [-0.1, 0.0, 0.2, 0.0, 0.2],  # More emotional and sophisticated
            "experimental": [-0.1, -0.2, 0.2, 0.1, 0.3], # More sophisticated and emotional
            "lo-fi": [-0.2, -0.1, 0.1, -0.2, 0.0],      # Less energetic
            "dark": [0.0, -0.1, 0.2, 0.2, 0.1],         # More emotional and intense
            "chill": [-0.2, -0.1, 0.1, -0.2, 0.0]       # Less energetic and intense
        }

    def _get_base_genre(self, genre: str) -> str:
        """Trouve le genre de base le plus proche pour un genre donné"""
        genre_lower = genre.lower()

        # Recherche directe
        if genre_lower in self.base_characteristics:
            return genre_lower

        # Recherche par sous-chaîne
        for base_genre in self.base_characteristics:
            if base_genre in genre_lower:
                return base_genre

        # Association par similarité
        genre_mapping = {
            "punk": "rock",
            "house": "electronic",
            "techno": "electronic",
            "edm": "electronic",
            "hip hop": "rap",
            "r&b": "soul",
            "alt": "rock",
            "indie": "rock",
            "core": "metal",
            "wave": "electronic"
        }

        for key, value in genre_mapping.items():
            if key in genre_lower:
                return value

        return "pop"  # Genre le plus générique comme dernier recours

    def _apply_modifiers(self, base_characteristics: np.ndarray, genre: str) -> np.ndarray:
        """Applique les modificateurs de genre aux caractéristiques de base"""
        characteristics = base_characteristics.copy()

        for modifier, changes in self.genre_modifiers.items():
            if modifier in genre.lower():
                characteristics += np.array(changes)

        # Normaliser les valeurs entre 0 et 1
        return np.clip(characteristics, 0, 1)

    def _get_genre_characteristics(self, genre: str) -> np.ndarray:
        """Calcule les caractéristiques musicales pour un genre donné"""
        base_genre = self._get_base_genre(genre)
        base_characteristics = np.array(self.base_characteristics[base_genre])
        return self._apply_modifiers(base_characteristics, genre)

    def _calculate_playlist_characteristics(self, genres_with_weights: List[Tuple[List[str], float]]) -> np.ndarray:
        """Calcule les caractéristiques moyennes pondérées de la playlist"""
        total_characteristics = np.zeros(5)
        total_weight = 0.0

        for genres, weight in genres_with_weights:
            for genre in genres:
                characteristics = self._get_genre_characteristics(genre)
                total_characteristics += characteristics * weight
                total_weight += weight

        if total_weight > 0:
            return total_characteristics / total_weight
        return np.array([0.5, 0.5, 0.5, 0.5, 0.5])

    def _calculate_mood_scores(self, characteristics: np.ndarray) -> Dict[str, float]:
        """Calcule les scores pour chaque mood basé sur les caractéristiques musicales"""
        # Définition des critères pour chaque mood
        mood_criteria = {
            "energetic": lambda c: (c[0] * 0.5 + c[1] * 0.3 + c[3] * 0.2) * 100,
            "chill": lambda c: ((1 - c[0]) * 0.4 + (1 - c[3]) * 0.3 + c[2] * 0.3) * 100,
            "romantic": lambda c: (c[2] * 0.5 + (1 - c[3]) * 0.3 + c[4] * 0.2) * 100,
            "dark": lambda c: (c[3] * 0.4 + (1 - c[2]) * 0.3 + (1 - c[1]) * 0.3) * 100,
            "sophisticated": lambda c: (c[4] * 0.5 + c[2] * 0.3 + (1 - c[1]) * 0.2) * 100,
            "intense": lambda c: (c[3] * 0.4 + c[0] * 0.4 + (1 - c[4]) * 0.2) * 100
        }

        # Calculer les scores bruts
        raw_scores = {
            mood: criteria(characteristics)
            for mood, criteria in mood_criteria.items()
        }

        # Normaliser les scores
        total_score = sum(raw_scores.values())
        if total_score > 0:
            normalized_scores = {
                mood: round((score / total_score) * 100, 1)
                for mood, score in raw_scores.items()
            }
            return normalized_scores

        return {mood: 0.0 for mood in mood_criteria.keys()}

    def analyze_artists(self, top_artists: List[Tuple[str, int, List[str]]]) -> Dict[str, float]:
        """Analyse les artistes et leurs genres pour déterminer les moods dominants"""
        if not top_artists:
            return {
                "energetic": 0.0,
                "chill": 0.0,
                "romantic": 0.0,
                "dark": 0.0,
                "sophisticated": 0.0,
                "intense": 0.0
            }

        total_count = sum(count for _, count, _ in top_artists)
        genres_with_weights = []

        for _, count, genres in top_artists:
            weight = count / total_count
            if genres:
                genres_with_weights.append((genres, weight))

        characteristics = self._calculate_playlist_characteristics(genres_with_weights)
        mood_scores = self._calculate_mood_scores(characteristics)

        logging.debug(f"Calculated characteristics: {characteristics}")
        logging.debug(f"Calculated mood scores: {mood_scores}")
        return mood_scores

    def get_dominant_moods(self, mood_scores: Dict[str, float], threshold: float = 15.0) -> List[str]:
        """Retourne les moods dominants (ceux dépassant le seuil)"""
        dominant_moods = [
            mood for mood, score in mood_scores.items() 
            if score >= threshold
        ]

        if not dominant_moods:
            sorted_moods = sorted(mood_scores.items(), key=lambda x: x[1], reverse=True)
            return [mood for mood, _ in sorted_moods[:2]]

        return dominant_moods