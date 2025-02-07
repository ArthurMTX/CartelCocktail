from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import logging
import os
from spotify_client import SpotifyClient
from cocktail_client import CocktailClient
from mood_analyzer import MoodAnalyzer
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
logging.basicConfig(level=logging.DEBUG)

try:
    spotify_client = SpotifyClient()
    cocktail_client = CocktailClient()
    mood_analyzer = MoodAnalyzer()
except Exception as e:
    logging.error(f"Failed to initialize clients: {str(e)}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    playlist_url = request.form.get('playlist_url')
    if not playlist_url:
        return render_template('index.html', error="Please provide a Spotify playlist URL")

    try:
        if not hasattr(app, 'spotify_client'):
            app.spotify_client = SpotifyClient()
        if not hasattr(app, 'cocktail_client'):
            app.cocktail_client = CocktailClient()
        if not hasattr(app, 'mood_analyzer'):
            app.mood_analyzer = MoodAnalyzer()

        # Get top artists and their genres from playlist
        top_artists = app.spotify_client.get_playlist_top_artists(playlist_url)
        logging.debug(f"Top artists: {top_artists}")

        # Analyze the moods and get detailed characteristics
        total_count = sum(count for _, count, _ in top_artists)
        genres_with_weights = []
        for _, count, genres in top_artists:
            weight = count / total_count
            if genres:
                genres_with_weights.append((genres, weight))
            else:
                genres_with_weights.append((["pop"], weight))

        # Get detailed characteristics
        characteristics = app.mood_analyzer._calculate_playlist_characteristics(genres_with_weights)
        characteristics_list = characteristics.tolist()  # Convert numpy array to list for JSON serialization

        # Calculate mood scores based on characteristics
        mood_scores = app.mood_analyzer._calculate_mood_scores(characteristics)
        logging.debug(f"Mood scores: {mood_scores}")

        dominant_moods = app.mood_analyzer.get_dominant_moods(mood_scores)
        logging.debug(f"Dominant moods: {dominant_moods}")

        # Get cocktail recommendations based on mood scores
        cocktails = app.cocktail_client.get_cocktails_by_moods(mood_scores)
        logging.debug(f"Number of cocktails recommended: {len(cocktails)}")

        # Ensure we have some cocktails
        if not cocktails:
            logging.warning("No cocktails were returned, using fallback")
            cocktails = app.cocktail_client.get_cocktails_by_moods(
                {"energetic": 100.0}, num_cocktails=1
            )

        return render_template('results.html', 
                              artists=[(name, count) for name, count, _ in top_artists],
                              artist_genres=[(name, genres) for name, _, genres in top_artists],
                              mood_scores=mood_scores,
                              dominant_moods=dominant_moods,
                              characteristics=characteristics_list,
                              cocktails=cocktails)

    except Exception as e:
        error_message = str(e)
        if "token" in error_message.lower():
            error_message = "Failed to authenticate with Spotify. Please check the API credentials."
        elif "playlist" in error_message.lower():
            error_message = "Invalid playlist URL or playlist not found. Please check the URL and try again."
        else:
            error_message = "An error occurred while analyzing the playlist. Please try again later."

        logging.error(f"Error in analyze route: {str(e)}")
        return render_template('index.html', error=error_message)

@app.route('/visualization')
def visualization():
    return render_template('visualization.html')

@app.route('/api/visualization-data')
def visualization_data():
    # Calculer les connexions entre genres et cocktails
    nodes = []
    links = []

    # Ajouter les genres principaux
    main_genres = list(mood_analyzer.base_characteristics.keys())
    for genre in main_genres:
        nodes.append({
            "id": f"genre_{genre}",
            "name": genre.title(),
            "type": "genre"
        })

    # Ajouter les cocktails principaux de chaque mood
    cocktail_mapping = cocktail_client.mood_cocktail_mapping
    for mood, cocktails in cocktail_mapping.items():
        for cocktail in cocktails[:3]:  # Limiter à 3 cocktails par mood
            nodes.append({
                "id": f"cocktail_{cocktail}",
                "name": cocktail,
                "type": "cocktail"
            })

            # Créer des liens basés sur les caractéristiques
            for genre in main_genres:
                genre_chars = mood_analyzer._get_genre_characteristics(genre)
                mood_scores = mood_analyzer._calculate_mood_scores(genre_chars)

                if mood in mood_scores and mood_scores[mood] > 20:  # Seuil de connexion
                    links.append({
                        "source": f"genre_{genre}",
                        "target": f"cocktail_{cocktail}",
                        "value": mood_scores[mood] / 100  # Normaliser entre 0 et 1
                    })

    return jsonify({"nodes": nodes, "links": links})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)