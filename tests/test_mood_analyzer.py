# test_mood_analyzer.py
import pytest
import numpy as np
import numpy.testing as npt
from mood_analyzer import MoodAnalyzer

def test_get_base_genre():
    analyzer = MoodAnalyzer()
    # Test direct: le genre "pop" existe dans les caractéristiques de base.
    assert analyzer._get_base_genre("pop") == "pop"
    
    # Test par sous-chaîne : "pop rock" contient "pop" et doit retourner "pop".
    assert analyzer._get_base_genre("pop rock") == "pop"
    
    # Test via le mapping : "punk" doit être associé à "rock".
    assert analyzer._get_base_genre("punk") == "rock"
    
    # Test avec un genre inconnu qui doit renvoyer "pop" par défaut.
    assert analyzer._get_base_genre("unknown") == "pop"

def test_get_genre_characteristics_no_modifier():
    analyzer = MoodAnalyzer()
    # Pour le genre "pop", aucun modificateur ne s'applique
    characteristics = analyzer._get_genre_characteristics("pop")
    expected = np.array([0.8, 0.8, 0.6, 0.5, 0.6])
    npt.assert_array_almost_equal(characteristics, expected)

def test_get_genre_characteristics_with_modifier():
    analyzer = MoodAnalyzer()
    # Pour "pop dance", le modificateur "dance" s'applique :
    # Base "pop" : [0.8, 0.8, 0.6, 0.5, 0.6]
    # Modifier "dance" : [0.1, 0.3, -0.1, 0.0, -0.1]
    # Somme : [0.9, 1.1, 0.5, 0.5, 0.5] puis clipping => [0.9, 1.0, 0.5, 0.5, 0.5]
    characteristics = analyzer._get_genre_characteristics("pop dance")
    expected = np.array([0.9, 1.0, 0.5, 0.5, 0.5])
    npt.assert_array_almost_equal(characteristics, expected)

def test_calculate_playlist_characteristics():
    analyzer = MoodAnalyzer()
    # On simule une playlist avec deux groupes de genres et des poids respectifs
    # Exemple : 2 occurrences de "pop" et 1 occurrence de "rock".
    genres_with_weights = [
        (["pop"], 2.0),
        (["rock"], 1.0)
    ]
    # Caractéristiques attendues :
    # "pop" : [0.8, 0.8, 0.6, 0.5, 0.6]
    # "rock": [0.8, 0.5, 0.7, 0.8, 0.7]
    # Somme pondérée = 2*[0.8, 0.8, 0.6, 0.5, 0.6] + 1*[0.8, 0.5, 0.7, 0.8, 0.7]
    #                 = [2.4, 2.1, 1.9, 1.8, 1.9]
    # Moyenne = [2.4, 2.1, 1.9, 1.8, 1.9] / 3
    expected = np.array([2.4, 2.1, 1.9, 1.8, 1.9]) / 3.0
    characteristics = analyzer._calculate_playlist_characteristics(genres_with_weights)
    npt.assert_array_almost_equal(characteristics, expected, decimal=4)

def test_calculate_mood_scores():
    analyzer = MoodAnalyzer()
    # On prend un vecteur de caractéristiques connu.
    characteristics = np.array([0.8, 0.7, 0.63, 0.6, 0.63])
    mood_scores = analyzer._calculate_mood_scores(characteristics)
    
    # Vérifier que toutes les clés attendues sont présentes
    expected_keys = {"energetic", "chill", "romantic", "dark", "sophisticated", "intense"}
    assert set(mood_scores.keys()) == expected_keys
    
    # La somme des scores normalisés doit être égale à 100 (arrondi)
    total = sum(mood_scores.values())
    assert abs(total - 100) < 1e-5

def test_analyze_artists_empty():
    analyzer = MoodAnalyzer()
    # Pour une liste vide, on attend que tous les moods soient à 0.0
    result = analyzer.analyze_artists([])
    expected = {
        "energetic": 0.0,
        "chill": 0.0,
        "romantic": 0.0,
        "dark": 0.0,
        "sophisticated": 0.0,
        "intense": 0.0
    }
    assert result == expected

def test_analyze_artists_non_empty():
    analyzer = MoodAnalyzer()
    # Exemple avec deux artistes :
    # - "Artist1" avec 2 occurrences et les genres "pop dance"
    # - "Artist2" avec 1 occurrence et le genre "rock"
    artists = [
        ("Artist1", 2, ["pop dance"]),
        ("Artist2", 1, ["rock"])
    ]
    result = analyzer.analyze_artists(artists)
    expected_keys = {"energetic", "chill", "romantic", "dark", "sophisticated", "intense"}
    assert set(result.keys()) == expected_keys
    for score in result.values():
        assert isinstance(score, float)
    # La somme des scores doit être approximativement 100
    total = sum(result.values())
    assert abs(total - 100) < 1e-5

def test_get_dominant_moods_above_threshold():
    analyzer = MoodAnalyzer()
    # Cas où un mood dépasse le seuil de 15.0
    mood_scores = {
        "energetic": 50.0,
        "chill": 10.0,
        "romantic": 10.0,
        "dark": 10.0,
        "sophisticated": 10.0,
        "intense": 10.0
    }
    dominant = analyzer.get_dominant_moods(mood_scores, threshold=15.0)
    # Seul "energetic" est au-dessus du seuil
    assert dominant == ["energetic"]

def test_get_dominant_moods_fallback():
    analyzer = MoodAnalyzer()
    # Cas où aucun mood ne dépasse le seuil de 15.0
    # On s'attend alors à ce que la fonction renvoie les deux moods les mieux classés.
    mood_scores = {
        "energetic": 10.0,
        "chill": 10.0,
        "romantic": 10.0,
        "dark": 10.0,
        "sophisticated": 10.0,
        "intense": 10.0
    }
    dominant = analyzer.get_dominant_moods(mood_scores, threshold=15.0)
    # Comme tous les moods ont le même score, la méthode trie et retourne les deux premiers.
    # Avec l'ordre d'insertion, on attend ["energetic", "chill"]
    assert dominant == ["energetic", "chill"]
