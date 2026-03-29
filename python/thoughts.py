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


def open_thoughts(artist: str, album: str, thoughts_dir: Path) -> Path:
    """Create a timestamped thoughts file and open it in the editor.

    Waits for the user to close the file before returning.
    Returns the path to the created file.
    """
    today = date.today().isoformat()
    slug = _slugify(album)
    filename = f"{slug}_{today}.md"
    filepath = thoughts_dir / filename

    if not filepath.exists():
        content = (
            f"# {album} — {artist}\n"
            f"Date: {today}\n"
            "\n"
            "Rating: \n"
            "Notes:\n"
            "Paragraph:\n"
        )
        filepath.write_text(content, encoding="utf-8")

    _open_in_editor(filepath)
    return filepath


def _open_in_editor(filepath: Path) -> None:
    # Try VS Code first (--wait blocks until the tab is closed)
    try:
        result = subprocess.run(
            ["vi", "--wait", str(filepath)],
            check=True,
            timeout=300,
        )
        return
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass

    # Fallback: OS default opener, then prompt
    opener = "open" if sys.platform == "darwin" else "xdg-open"
    try:
        subprocess.run([opener, str(filepath)], check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass

    input(f"Edit {filepath} then press Enter when done...")


def read_thoughts(filepath: Path) -> dict:
    """Parse a thoughts file and return rating and notes."""
    text = filepath.read_text(encoding="utf-8")
    result = {"rating": "", "notes": "", "paragraph": ""}

    for line in text.splitlines():
        if line.startswith("Rating:"):
            result["rating"] = line[len("Rating:"):].strip()
        elif line.startswith("Notes:"):
            result["notes"] = line[len("Notes:"):].strip()
        elif line.startswith("Paragraph:"):
            result["paragraph"] = line[len("Paragraph:"):].strip()

    return result
