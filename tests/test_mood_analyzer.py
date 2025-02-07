import pytest
from mood_analyzer import MoodAnalyzer

def test_analyze_artists():
    analyzer = MoodAnalyzer()
    test_artists = [
        ("Artist1", 3, ["pop", "dance"]),
        ("Artist2", 2, ["rock", "metal"]),
        ("Artist3", 1, ["classical", "jazz"])
    ]

    mood_scores = analyzer.analyze_artists(test_artists)
    assert isinstance(mood_scores, dict)
    assert all(mood in mood_scores for mood in ["energetic", "chill", "romantic", "dark"])
    assert sum(mood_scores.values()) > 0

def test_genre_mood_mapping():
    analyzer = MoodAnalyzer()
    assert "pop" in analyzer.genre_mood_mapping
    assert "rock" in analyzer.genre_mood_mapping
    assert "energetic" in analyzer.genre_mood_mapping["pop"]

def test_calculate_mood_scores():
    analyzer = MoodAnalyzer()
    genres = ["pop", "rock"]
    weight = 1.0
    mood_scores = analyzer._calculate_mood_scores(genres, weight)
    assert isinstance(mood_scores, dict)
    assert all(mood in mood_scores for mood in ["energetic", "chill", "romantic", "dark"])