import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv

load_dotenv()


def get_spotify_client() -> spotipy.Spotify:
    """Authenticate with Spotify and return an authorized client.

    Uses Client Credentials flow (no user login required) since album search
    is a public endpoint. Credentials are read from .env:
      SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET
    """
    client_id = os.environ.get("SPOTIPY_CLIENT_ID")
    client_secret = os.environ.get("SPOTIPY_CLIENT_SECRET")

    if not client_id or not client_secret:
        raise EnvironmentError(
            "Missing Spotify credentials. "
            "Set SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET in a .env file."
        )

    auth_manager = SpotifyClientCredentials(
        client_id=client_id,
        client_secret=client_secret,
    )

    return spotipy.Spotify(auth_manager=auth_manager)
