import requests
import random
from typing import List, Dict, Any
from config import Config

class CocktailClient:
    def __init__(self):
        self.api_key = Config.COCKTAILDB_API_KEY
        self.base_url = "https://www.thecocktaildb.com/api/json/v1/1"

        # Mapping enrichi des moods vers les cocktails
        self.mood_cocktail_mapping = {
            "energetic": [
                "Margarita", "Mojito", "Long Island Iced Tea", 
                "Cosmopolitan", "Caipirinha", "Moscow Mule",
                "Paloma", "Gin Fizz", "Tequila Sunrise"
            ],
            "chill": [
                "Old Fashioned", "Negroni", "Manhattan", 
                "Whiskey Sour", "Mai Tai", "Gin and Tonic",
                "Aperol Spritz", "Dark 'n' Stormy", "Boulevardier"
            ],
            "romantic": [
                "Champagne Cocktail", "French 75", "Kir Royale",
                "Pink Lady", "Rose", "Bellini",
                "Aviation", "French Martini", "Clover Club"
            ],
            "dark": [
                "Black Russian", "Espresso Martini", "Godfather",
                "Blue Moon", "Death in the Afternoon", "Rusty Nail",
                "Blood and Sand", "El Diablo", "Jungle Bird"
            ]
        }

        # Caractéristiques des cocktails pour un meilleur matching
        self.cocktail_characteristics = {
            "energetic": ["refreshing", "citrus", "fizzy", "bright"],
            "chill": ["smooth", "balanced", "classic", "refined"],
            "romantic": ["elegant", "delicate", "floral", "sparkling"],
            "dark": ["bold", "complex", "intense", "mysterious"]
        }

    def get_cocktails_by_moods(self, mood_scores: Dict[str, float], num_cocktails: int = 3) -> List[Dict[str, Any]]:
        """
        Récupère des cocktails basés sur les scores de différents moods
        """
        # Ensure all mood scores are present with at least 0.0
        all_moods = ["energetic", "chill", "romantic", "dark"]
        mood_scores = {mood: mood_scores.get(mood, 0.0) for mood in all_moods}

        # Filter out moods with very low scores (less than 5%)
        significant_moods = {mood: score for mood, score in mood_scores.items() if score >= 5.0}

        # If no significant moods, use the highest scoring mood
        if not significant_moods:
            max_mood = max(mood_scores.items(), key=lambda x: x[1])
            significant_moods = {max_mood[0]: max_mood[1]}

        selected_cocktails = []
        for mood in significant_moods:
            # Select cocktails for each significant mood
            available_cocktails = self.mood_cocktail_mapping[mood]
            num_to_select = min(max(1, int(num_cocktails * significant_moods[mood] / 100)), len(available_cocktails))
            selected_names = random.sample(available_cocktails, num_to_select)

            for cocktail_name in selected_names:
                response = requests.get(f"{self.base_url}/search.php?s={cocktail_name}")
                if response.status_code == 200 and response.json().get("drinks"):
                    cocktail_data = response.json()["drinks"][0]
                    # Ajouter les caractéristiques du mood
                    cocktail_data["mood_characteristics"] = random.sample(
                        self.cocktail_characteristics[mood], 
                        k=min(2, len(self.cocktail_characteristics[mood]))
                    )
                    selected_cocktails.append(cocktail_data)

        # If we still don't have any cocktails, fallback to a default
        if not selected_cocktails:
            response = requests.get(f"{self.base_url}/search.php?s=Margarita")
            if response.status_code == 200 and response.json().get("drinks"):
                cocktail_data = response.json()["drinks"][0]
                cocktail_data["mood_characteristics"] = ["refreshing", "bright"]
                selected_cocktails.append(cocktail_data)

        return selected_cocktails