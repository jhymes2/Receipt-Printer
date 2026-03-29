import re
import subprocess
import sys
from datetime import date
from pathlib import Path


def _slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = text.strip("-")
    return text


def open_thoughts(artist: str, album: str, thoughts_dir: Path, tracks: list[dict] | None = None) -> Path:
    """Create a timestamped thoughts file and open it in the editor.

    Waits for the user to close the file before returning.
    Returns the path to the created file.
    """
    today = date.today().isoformat()
    slug = _slugify(album)
    filename = f"{slug}_{today}.md"
    filepath = thoughts_dir / filename

    if not filepath.exists():
        track_ref = ""
        if tracks:
            lines = ["\n\n---"]
            for t in tracks:
                lines.append(f"{t['number']:2d}. {t['title']}")
            track_ref = "\n".join(lines)
        content = (
            f"# {album} — {artist}\n"
            f"Date: {today}\n"
            "\n"
            "Rating: \n"
            "Fav: \n"
            "Notes:\n"
            f"{track_ref}\n"
        )
        filepath.write_text(content, encoding="utf-8")

    _open_in_editor(filepath)
    return filepath


def _open_in_editor(filepath: Path) -> None:
    subprocess.run(["vi", str(filepath)], check=True)


def read_thoughts(filepath: Path) -> dict:
    """Parse a thoughts file and return rating, fav_track, and notes."""
    text = filepath.read_text(encoding="utf-8")
    result = {"rating": "", "fav_track": [], "notes": "", "paragraph": ""}

    for line in text.splitlines():
        if line.startswith("Rating:"):
            result["rating"] = line[len("Rating:"):].strip()
        elif line.startswith("Fav:"):
            fav = line[len("Fav:"):].strip()
            result["fav_track"] = [fav] if fav else []
        elif line.startswith("Notes:"):
            result["notes"] = line[len("Notes:"):].strip()
        elif line.startswith("Paragraph:"):
            result["paragraph"] = line[len("Paragraph:"):].strip()

    return result
