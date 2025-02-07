# test_cocktail_client.py
import pytest
import random
from unittest.mock import patch, MagicMock
from cocktail_client import CocktailClient

# Classe helper pour simuler les réponses de requests.get
class DummyResponse:
    def __init__(self, status_code, json_data):
        self.status_code = status_code
        self._json_data = json_data

    def json(self):
        return self._json_data

# Fonction de side effect pour simuler une réponse valide pour un cocktail donné
def fake_requests_get(url, *args, **kwargs):
    if "s=" in url:
        cocktail_name = url.split("s=")[-1]
        return DummyResponse(200, {"drinks": [{"strDrink": cocktail_name, "idDrink": "12345"}]})
    return DummyResponse(404, {})

# Nouvelle fonction de side effect qui compte les appels :
def fake_requests_get_no_drinks_counter():
    call_count = [0]
    def side_effect(url, *args, **kwargs):
        call_count[0] += 1
        if call_count[0] == 1:
            # Simuler l'absence de cocktail lors de l'appel dans la boucle
            return DummyResponse(200, {"drinks": None})
        else:
            # Pour l'appel de fallback, si l'URL contient "Margarita", renvoyer une réponse valide
            if "Margarita" in url:
                return DummyResponse(200, {"drinks": [{"strDrink": "Margarita", "idDrink": "fallback"}]})
            else:
                return DummyResponse(200, {"drinks": None})
    return side_effect

# Fixture pour instancier CocktailClient en patchant la configuration si nécessaire
@pytest.fixture
def cocktail_client():
    with patch('cocktail_client.Config') as mock_config:
        mock_config.COCKTAILDB_API_KEY = "dummy_key"
        yield CocktailClient()

# Patch automatique de random.sample pour garantir un comportement déterministe
@pytest.fixture(autouse=True)
def patch_random_sample():
    with patch('cocktail_client.random.sample', side_effect=lambda x, k: x[:k]):
        yield

def test_get_cocktails_by_moods_significant(cocktail_client):
    mood_scores = {
        "energetic": 50.0,
        "chill": 3.0,
        "romantic": 2.0,
        "dark": 0.0
    }
    with patch('cocktail_client.requests.get', side_effect=fake_requests_get):
        cocktails = cocktail_client.get_cocktails_by_moods(mood_scores, num_cocktails=3)
        assert len(cocktails) >= 1
        for cocktail in cocktails:
            assert 'strDrink' in cocktail
            assert 'mood_characteristics' in cocktail
            assert len(cocktail['mood_characteristics']) <= 2

def test_get_cocktails_by_moods_no_significant(cocktail_client):
    mood_scores = {
        "energetic": 3.0,
        "chill": 2.0,
        "romantic": 1.0,
        "dark": 0.0
    }
    with patch('cocktail_client.requests.get', side_effect=fake_requests_get):
        cocktails = cocktail_client.get_cocktails_by_moods(mood_scores, num_cocktails=3)
        assert len(cocktails) >= 1
        for cocktail in cocktails:
            assert 'strDrink' in cocktail
            assert 'mood_characteristics' in cocktail

def test_get_cocktails_by_moods_fallback(cocktail_client):
    """
    Simule le cas où aucune requête ne retourne de cocktail lors de la boucle,
    forçant ainsi le mécanisme de fallback.
    """
    mood_scores = {
        "energetic": 50.0,
        "chill": 0.0,
        "romantic": 0.0,
        "dark": 0.0
    }
    side_effect = fake_requests_get_no_drinks_counter()
    with patch('cocktail_client.requests.get', side_effect=side_effect):
        cocktails = cocktail_client.get_cocktails_by_moods(mood_scores, num_cocktails=3)
        # Le fallback doit renvoyer le cocktail "Margarita" avec des caractéristiques fixes
        assert len(cocktails) == 1
        cocktail = cocktails[0]
        assert "Margarita" in cocktail.get("strDrink", "")
        assert cocktail.get("mood_characteristics") == ["refreshing", "bright"]
