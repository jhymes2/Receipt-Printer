# PROJECT STRUCTURE

/spotify-receipt/
/python/
main.py ← entry point, orchestrates everything
spotify_auth.py ← OAuth login + token cache
spotify_fetch.py ← album search + track data
receipt_builder.py ← formats data into receipt layout
thoughts.py ← opens/archives thoughts.md
/arduino/
src/
main.cpp ← PlatformIO entry point
receipt_print.cpp ← Adafruit_Thermal print logic
receipt_print.h
lib/
Adafruit_Thermal/ ← drop library here
platformio.ini
/receipts/ ← archived .md receipts
/thoughts/ ← archived thoughts by album

═══════════════════════════════════════
PYTHON SIDE (runs on your computer)
═══════════════════════════════════════

1. STARTUP [main.py]
   - spotify_auth.py: check for cached token
     - if none → open browser for Spotify OAuth login
     - save token to .cache file

2. ALBUM SEARCH [main.py + spotify_fetch.py]
   - prompt: "Search for album: "
   - call Spotify API → search albums
   - if multiple results:
     display numbered list (name, artist, year)
     prompt: "Pick a number: "
   - fetch full album data:
     album_name, artist, year
     tracks[ {number, title, duration_ms} ]
     total_duration_ms

3. THOUGHTS [thoughts.py]
   - create /thoughts/ALBUM-NAME_TIMESTAMP.md with template:
     # [Album Name] - [Artist]
     Rating: /10
     Favorite Track:
     Notes:
   - open file in default editor (os.system / subprocess)
   - prompt: "Press Enter when done writing thoughts..."
   - read file back in → parse rating, fav track, notes

4. RECEIPT PREVIEW [receipt_builder.py]
   - format receipt as text in terminal:
     ================================
     ARTIST NAME
     Album Title (Year)
     ================================
     1. Track Title 3:24
     2. Track Title 4:11
        ...
        ================================
        Total 42:17
        ================================
        Rating: 8/10
        Fav Track: Track Title
        Notes: great album
        ================================
   - prompt: "Print this? (y/n)"

5. GENERATE ARDUINO DATA [receipt_builder.py]
   - write /arduino/src/receipt_data.h:
     // AUTO-GENERATED — do not edit
     const char* ARTIST = "Radiohead";
     const char* ALBUM = "OK Computer";
     const char* YEAR = "1997";
     const char TRACKS[][2] = {
     {"Airbag", "4:44"},
     {"Paranoid Android", "6:23"},
     ...
     };
     const int TRACK_COUNT = 12;
     const char* TOTAL_TIME = "53:21";
     const char* RATING = "9/10";
     const char* FAV_TRACK = "Exit Music";
     const char\* NOTES = "classic";
   - save human-readable copy to /receipts/ALBUM-NAME.md

6. BUILD + UPLOAD [main.py]
   - run: subprocess → "pio run --target upload"
     (PlatformIO CLI compiles main.cpp and uploads to Arduino)
   - confirm: "Printing..."

═══════════════════════════════════════
C++ / ARDUINO SIDE (runs on the board)
═══════════════════════════════════════

7. PRINT RECEIPT [main.cpp + receipt_print.cpp]

   setup():
   - init SoftwareSerial on TX/RX pins
   - printer.begin()
   - call printReceipt()
   - printer.sleep()

   printReceipt():
   - printer.justify('C')
   - printer.boldOn() + printer.setSize('M')
   - printer.println(ARTIST)
   - printer.boldOff()
   - printer.println(ALBUM + " (" + YEAR + ")")
   - printer.setSize('S')
   - print divider "─────────────────────"

   - printer.justify('L')
   - for each track in TRACKS[]:
     print "N. Title" left-aligned
     print duration right-aligned (pad with spaces)

   - print divider
   - print "Total" + TOTAL_TIME
   - print divider

   - printer.println("Rating: " + RATING)
   - printer.println("Fav: " + FAV_TRACK)
   - printer.println(NOTES)
   - printer.feed(3)

   loop(): (empty — one-shot print on boot)
