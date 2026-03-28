/spotify-receipt/
│
├── python/ ← Python never touches anything in arduino/src
│ ├── main.py
│ ├── spotify_auth.py
│ ├── spotify_fetch.py
│ ├── receipt_builder.py ← ONLY file that writes receipt_data.h
│ └── thoughts.py
│
├── arduino/ ← C++ never touches anything in python/
│ ├── platformio.ini
│ ├── lib/
│ │ └── Adafruit_Thermal/ ← library lives here, never modified
│ └── src/
│ ├── main.cpp ← never edited by hand or Python
│ ├── receipt_print.cpp ← never edited by hand or Python
│ ├── receipt_print.h ← never edited by hand or Python
│ └── receipt_data.h ← ⬅ THE HANDOFF FILE (Python writes, C++ reads)
│
├── receipts/ ← Python writes, no one else touches
│ ├── ok-computer.md
│ └── in-rainbows.md
│
└── thoughts/ ← Python writes, user edits, no one else touches
├── ok-computer_2024-03-01.md
└── in-rainbows_2024-03-15.md
