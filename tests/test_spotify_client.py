import pytest
from spotify_client import SpotifyClient
from unittest.mock import patch, MagicMock

@pytest.fixture
def spotify_client():
    return SpotifyClient()

def test_get_token(spotify_client):
    with patch('requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"access_token": "test-token"}
        mock_post.return_value = mock_response
        token = spotify_client._get_token()
        assert token == "test-token"

def test_get_playlist_top_artists(spotify_client):
    with patch('requests.get') as mock_get:
        # Mock pour la requête de playlist
        playlist_response = MagicMock()
        playlist_response.status_code = 200
        playlist_response.json.return_value = {
            "items": [
                {"track": {"artists": [{"id": "artist1", "name": "Artist1"}]}},
                {"track": {"artists": [{"id": "artist1", "name": "Artist1"}]}},
                {"track": {"artists": [{"id": "artist2", "name": "Artist2"}]}}
            ]
        }

        # Mock pour la requête des détails d'artiste
        artist_response = MagicMock()
        artist_response.status_code = 200
        artist_response.json.return_value = {
            "name": "Artist1",
            "genres": ["pop", "dance"]
        }

        # Configuration du mock pour retourner différentes réponses
        def get_side_effect(url, **kwargs):
            if "playlists" in url:
                return playlist_response
            return artist_response

        mock_get.side_effect = get_side_effect

        top_artists = spotify_client.get_playlist_top_artists("playlist_url")
        assert len(top_artists) <= 5
        assert isinstance(top_artists[0], tuple)
        assert len(top_artists[0]) == 3  # (name, count, genres)
        assert top_artists[0][0] == "Artist1"
        assert top_artists[0][1] == 2  # count
        assert isinstance(top_artists[0][2], list)  # genres