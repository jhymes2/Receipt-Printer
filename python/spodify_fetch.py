import os
import urllib.parse
import urllib.request
import json

from spodify_auth import get_spotify_client


def _lastfm_album_info(artist: str, album: str) -> dict:
    """Fetch album info from Last.fm. Returns genres and playcount."""
    api_key = os.environ.get("LASTFM_API_KEY", "")
    if not api_key or api_key == "your_lastfm_api_key_here":
        return {"genres": [], "popularity": None}
    params = urllib.parse.urlencode({
        "method": "album.getInfo",
        "api_key": api_key,
        "artist": artist,
        "album": album,
        "format": "json",
        "autocorrect": 1,
    })
    try:
        with urllib.request.urlopen(
            f"https://ws.audioscrobbler.com/2.0/?{params}", timeout=5
        ) as resp:
            data = json.loads(resp.read())
        info = data.get("album", {})
        tags = info.get("tags", {}).get("tag", [])
        genres = [t["name"] for t in tags[:3]]
        playcount = info.get("playcount")
        return {"genres": genres, "popularity": int(playcount) if playcount else None}
    except Exception:
        return {"genres": [], "popularity": None}


def _ms_to_mss(ms: int) -> str:
    total_seconds = ms // 1000
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    return f"{minutes}:{seconds:02d}"


def _ms_to_total(total_ms: int) -> str:
    total_seconds = total_ms // 1000
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    if hours > 0:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    return f"{minutes}:{seconds:02d}"


def search_album(query: str) -> list[dict]:
    """Search Spotify for albums matching query.

    Returns a list of candidate dicts with keys: id, name, artist, year.
    """
    sp = get_spotify_client()
    try:
        results = sp.search(q=query, type="album", limit=10)
    except Exception as e:
        print(f"Spotify search failed: {e}")
        raise SystemExit(1)

    items = results.get("albums", {}).get("items", [])
    candidates = []
    for item in items:
        artist = item["artists"][0]["name"] if item["artists"] else "Unknown"
        year = item.get("release_date", "")[:4]
        candidates.append({
            "id": item["id"],
            "name": item["name"],
            "artist": artist,
            "year": year,
        })
    return candidates


def get_album_data(album_id: str) -> dict:
    """Fetch full album data from Spotify and return a structured dict.

    Returns:
        {
          "artist": str,
          "album": str,
          "year": str,
          "tracks": [{"number": int, "title": str, "duration": str}],
          "total_duration": str,
        }
    """
    sp = get_spotify_client()
    try:
        album = sp.album(album_id)
    except Exception as e:
        print(f"Failed to fetch album data: {e}")
        raise SystemExit(1)

    artist_obj = album["artists"][0] if album["artists"] else {}
    artist = artist_obj.get("name", "Unknown")
    name = album["name"]
    year = album.get("release_date", "")[:4]

    lastfm = _lastfm_album_info(artist, name)
    genres = lastfm["genres"]
    popularity = lastfm["popularity"]

    track_items = album["tracks"]["items"]
    tracks = []
    total_ms = 0
    for item in track_items:
        duration_ms = item.get("duration_ms", 0)
        total_ms += duration_ms
        tracks.append({
            "number": item["track_number"],
            "title": item["name"],
            "duration": _ms_to_mss(duration_ms),
        })

    return {
        "artist": artist,
        "genres": genres,
        "popularity": popularity,
        "album": name,
        "year": year,
        "tracks": tracks,
        "total_duration": _ms_to_total(total_ms),
    }
