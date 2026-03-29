import io
import os
import re
import subprocess
import sys
import termios
import tty
from contextlib import redirect_stdout
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

# Load .env from python/ directory
load_dotenv(Path(__file__).parent / ".env")

# Project root is one level above python/
ROOT = Path(__file__).parent.parent

from spodify_fetch import get_album_data, search_album  # noqa: E402
from receipt_builder import (  # noqa: E402
    archive_receipt,
    generate_header_file,
    preview_receipt,
)
from thoughts import open_thoughts, read_thoughts  # noqa: E402


def _input_or_esc(prompt: str) -> str:
    """Like input() but exits immediately if ESC is pressed."""
    print(prompt, end="", flush=True)
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    chars: list[str] = []
    try:
        tty.setraw(fd)
        while True:
            ch = sys.stdin.read(1)
            if ch == "\x1b":
                print()
                raise SystemExit(0)
            elif ch in ("\r", "\n"):
                print()
                return "".join(chars)
            elif ch in ("\x7f", "\x08"):  # backspace
                if chars:
                    chars.pop()
                    print("\b \b", end="", flush=True)
            elif ch.isprintable():
                chars.append(ch)
                print(ch, end="", flush=True)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


def pick_album(candidates: list[dict]) -> dict:
    if not candidates:
        print("No albums found.")
        raise SystemExit(1)

    if len(candidates) == 1:
        a = candidates[0]
        print(f"Found: {a['name']} by {a['artist']} ({a['year']})")
        return a

    print("\nResults:")
    for i, a in enumerate(candidates, 1):
        print(f"  {i}. {a['name']} — {a['artist']} ({a['year']})")

    while True:
        raw = _input_or_esc("\nPick an album (number): ").strip()
        if raw.isdigit() and 1 <= int(raw) <= len(candidates):
            return candidates[int(raw) - 1]
        print(f"Enter a number between 1 and {len(candidates)}.")



def _pio() -> str:
    """Return the pio executable path, searching common install locations."""
    candidates = [
        Path.home() / ".platformio" / "penv" / "bin" / "pio",
        Path("/usr/local/bin/pio"),
        Path("/opt/homebrew/bin/pio"),
    ]
    for p in candidates:
        if p.exists():
            return str(p)
    return "pio"  # fall back to PATH


def upload_to_printer(arduino_dir: Path) -> None:
    print("\nUploading to printer...")
    proc = subprocess.Popen(
        [_pio(), "run", "--target", "upload"],
        cwd=str(arduino_dir),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    for line in proc.stdout:
        print(line, end="")
    proc.wait()
    if proc.returncode != 0:
        print(f"\nUpload failed (exit code {proc.returncode}).")
        print("Tip: run `pio device list` to check the port.")
        raise SystemExit(proc.returncode)
    print("Done! Receipt printed.")


def main() -> None:
    query = input("Search album: ").strip()
    if not query:
        raise SystemExit(0)

    print("Searching Spotify...")
    candidates = search_album(query)
    chosen = pick_album(candidates)

    print(f"\nFetching track data for '{chosen['name']}'...")
    album_data = get_album_data(chosen["id"])

    thoughts_dir = ROOT / "thoughts"
    thoughts_path = open_thoughts(
        album_data["artist"], album_data["album"], thoughts_dir, album_data["tracks"]
    )
    thoughts_data = read_thoughts(thoughts_path)
    # Resolve fav track numbers to titles ("3 7 11" → [title3, title7, title11])
    fav_str = (thoughts_data["fav_track"] or [""])[0]
    if fav_str:
        track_map = {t["number"]: t["title"] for t in album_data["tracks"]}
        nums = [int(tok) for tok in fav_str.split() if tok.isdigit() and int(tok) in track_map]
        thoughts_data["fav_track"] = [track_map[n] for n in nums]

    # Capture preview text, then print it
    buf = io.StringIO()
    with redirect_stdout(buf):
        preview_receipt(album_data, thoughts_data)
    preview_text = buf.getvalue()

    os.system("clear" if sys.platform != "win32" else "cls")
    print(preview_text, end="")

    answer = input("\nPrint this? (y/n): ").strip().lower()
    if answer != "y":
        print("Cancelled.")
        raise SystemExit(0)

    header_path = ROOT / "arduino" / "src" / "receipt_data.h"
    generate_header_file(album_data, thoughts_data, header_path)
    print(f"Generated {header_path.relative_to(ROOT)}")

    receipt_path = archive_receipt(album_data, thoughts_data, ROOT / "receipts")
    print(f"Archived receipt → {receipt_path.relative_to(ROOT)}")

    slug = re.sub(r"[^\w\s-]", "", album_data["album"].lower())
    slug = re.sub(r"[\s_]+", "-", slug).strip("-")
    fmt_dir = ROOT / "format-receipts"
    fmt_dir.mkdir(exist_ok=True)
    fmt_path = fmt_dir / f"{slug}_{date.today().isoformat()}.txt"
    fmt_path.write_text(preview_text, encoding="utf-8")
    print(f"Saved preview → {fmt_path.relative_to(ROOT)}")

    upload_to_printer(ROOT / "arduino")


if __name__ == "__main__":
    main()
