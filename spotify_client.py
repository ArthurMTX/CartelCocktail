import requests
import base64
import logging
from config import Config

class SpotifyClient:
    def __init__(self):
        self.client_id = Config.SPOTIFY_CLIENT_ID
        self.client_secret = Config.SPOTIFY_CLIENT_SECRET
        self.token = None
        try:
            self.token = self._get_token()
        except Exception as e:
            logging.error(f"Failed to initialize Spotify client: {str(e)}")
            raise

    def _get_token(self):
        auth_string = f"{self.client_id}:{self.client_secret}"
        auth_bytes = auth_string.encode("utf-8")
        auth_base64 = base64.b64encode(auth_bytes).decode("utf-8")

        headers = {
            "Authorization": f"Basic {auth_base64}",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        data = {"grant_type": "client_credentials"}
        response = requests.post("https://accounts.spotify.com/api/token", headers=headers, data=data)

        if response.status_code != 200:
            error_msg = f"Failed to get Spotify token. Status: {response.status_code}"
            try:
                error_msg += f", Details: {response.json()}"
            except:
                pass
            logging.error(error_msg)
            raise Exception(error_msg)

        token_data = response.json()
        if "access_token" not in token_data:
            error_msg = f"Invalid token response: {token_data}"
            logging.error(error_msg)
            raise Exception(error_msg)

        return token_data["access_token"]

    def get_artist_details(self, artist_id):
        """Récupère les détails d'un artiste, y compris ses genres"""
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(f"https://api.spotify.com/v1/artists/{artist_id}", headers=headers)

        if response.status_code != 200:
            logging.error(f"Failed to get artist details. Status: {response.status_code}")
            return {"name": "", "genres": []}

        artist_data = response.json()
        return {
            "name": artist_data.get("name", ""),
            "genres": artist_data.get("genres", [])
        }
    
    def get_playlist_info(self, playlist_url):
        if not self.token:
            raise Exception("Spotify client not properly initialized")

        try:
            playlist_id = playlist_url.split('/')[-1].split('?')[0]
            headers = {"Authorization": f"Bearer {self.token}"}

            response = requests.get(f"https://api.spotify.com/v1/playlists/{playlist_id}", headers=headers)

            if response.status_code != 200:
                error_msg = f"Failed to get playlist. Status: {response.status_code}"
                try:
                    error_msg += f", Details: {response.json()}"
                except:
                    pass
                logging.error(error_msg)
                raise Exception(error_msg)

            playlist_data = response.json()
            return {
                "name": playlist_data.get("name", ""),
                "description": playlist_data.get("description", ""),
                "owner": playlist_data.get("owner", {}).get("display_name", ""),
                "image": playlist_data.get("images", [{}])[0].get("url", "")
            }

        except Exception as e:
            logging.error(f"Error getting playlist info: {str(e)}")
            raise

    def get_playlist_top_artists(self, playlist_url):
        if not self.token:
            raise Exception("Spotify client not properly initialized")

        try:
            playlist_id = playlist_url.split('/')[-1].split('?')[0]
            headers = {"Authorization": f"Bearer {self.token}"}

            response = requests.get(f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks", headers=headers)

            if response.status_code != 200:
                error_msg = f"Failed to get playlist. Status: {response.status_code}"
                try:
                    error_msg += f", Details: {response.json()}"
                except:
                    pass
                logging.error(error_msg)
                raise Exception(error_msg)

            tracks = response.json()["items"]

            artists_data = {}
            for track in tracks:
                if track.get("track") and track["track"].get("artists"):
                    artist = track["track"]["artists"][0]
                    artist_id = artist["id"]
                    if artist_id not in artists_data:
                        artist_details = self.get_artist_details(artist_id)
                        artists_data[artist_id] = {
                            "name": artist_details["name"],
                            "count": 1,
                            "genres": artist_details["genres"]
                        }
                    else:
                        artists_data[artist_id]["count"] += 1

            # Convert to list of tuples (name, count, genres)
            artists_list = [(data["name"], data["count"], data["genres"]) 
                          for data in artists_data.values()]

            # Sort by count and take top 5
            return sorted(artists_list, key=lambda x: x[1], reverse=True)[:5]

        except Exception as e:
            logging.error(f"Error getting playlist artists: {str(e)}")
            raise