from spodify_auth import get_spotify_client


def main():
    print("Connecting to Spotify...")
    sp = get_spotify_client()

    # Verify auth with a basic search (no scopes required)
    results = sp.search(q="Radiohead OK Computer", type="album", limit=1)
    album = results["albums"]["items"][0]
    print(f"Auth successful. Test query returned: {album['name']} by {album['artists'][0]['name']}")


if __name__ == "__main__":
    main()
