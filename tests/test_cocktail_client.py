import pytest
from cocktail_client import CocktailClient
from unittest.mock import patch

@pytest.fixture
def cocktail_client():
    return CocktailClient()

def test_get_cocktails_by_moods(cocktail_client):
    with patch('requests.get') as mock_get:
        mock_response = {
            "drinks": [{
                "strDrink": "Margarita",
                "strDrinkThumb": "url",
                "strInstructions": "Mix ingredients"
            }]
        }
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response

        mood_scores = {"energetic": 100.0, "chill": 0.0, "romantic": 0.0, "dark": 0.0}
        cocktails = cocktail_client.get_cocktails_by_moods(mood_scores)
        assert len(cocktails) > 0
        assert cocktails[0]["strDrink"] == "Margarita"