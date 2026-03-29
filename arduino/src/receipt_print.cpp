#include "receipt_print.h"
#include "receipt_data.h"

// Serial pins — ESP32 UART1 (for Arduino Uno use TX=6, RX=5)
#define TX_PIN 17
#define RX_PIN 16

HardwareSerial printerSerial(1);
Adafruit_Thermal printer(&printerSerial);

// ── string helpers ────────────────────────────────────────────────────────────

// Left label, right value, total LINE_WIDTH chars. Truncates label if needed.
String padLine(const char* left, const char* right) {
  int rightLen = strlen(right);
  int leftMax  = LINE_WIDTH - rightLen;
  String label = String(left);
  if ((int)label.length() > leftMax) {
    label = label.substring(0, leftMax - 2) + "..";
  }
  int spaces = LINE_WIDTH - (int)label.length() - rightLen;
  String line = label;
  for (int i = 0; i < spaces; i++) line += ' ';
  line += String(right);
  return line;
}

// Centers text within LINE_WIDTH, padding both sides with spaces.
String centerLine(const char* text) {
  int len   = strlen(text);
  int total = LINE_WIDTH - len;
  int left  = total / 2;
  int right = total - left;
  String line = "";
  for (int i = 0; i < left;  i++) line += ' ';
  line += String(text);
  for (int i = 0; i < right; i++) line += ' ';
  return line;
}

// Full-width divider.
String dividerLine() {
  String line = "";
  for (int i = 0; i < LINE_WIDTH; i++) line += '=';
  return line;
}

// Formats a large number with comma separators (e.g. 250678057 → "250,678,057").
String formatLong(unsigned long n) {
  String s = String(n);
  int pos = (int)s.length() - 3;
  while (pos > 0) {
    s = s.substring(0, pos) + "," + s.substring(pos);
    pos -= 3;
  }
  return s;
}

// ── printer setup ─────────────────────────────────────────────────────────────

void initPrinter() {
  printerSerial.begin(19200, SERIAL_8N1, RX_PIN, TX_PIN);
  // If printer doesn't respond, try: printerSerial.begin(9600, SERIAL_8N1, RX_PIN, TX_PIN);
  printer.begin();
  printer.setFont('A');
  printer.justify('L');   // always L — padding handles all alignment
  printer.setSize('S');
}

// ── receipt ───────────────────────────────────────────────────────────────────

void printReceipt() {
  // header
  printer.println(dividerLine());
  printer.boldOn();
  printer.setSize('M');
  printer.println(centerLine(ARTIST));
  printer.boldOff();
  printer.setSize('S');

  char albumYear[84];
  snprintf(albumYear, sizeof(albumYear), "%s (%s)", ALBUM, YEAR);
  printer.println(centerLine(albumYear));
  printer.println(centerLine(TAGS));

  String playsStr = formatLong(POPULARITY) + " plays";
  printer.println(centerLine(playsStr.c_str()));
  printer.println(dividerLine());

  // tracks
  for (int i = 0; i < TRACK_COUNT; i++) {
    char label[50];
    snprintf(label, sizeof(label), " %2d. %s", i + 1, TRACKS[i][0]);
    printer.println(padLine(label, TRACKS[i][1]));
  }

  // total
  printer.println(dividerLine());
  printer.println(padLine(" Total", TOTAL_TIME));
  printer.println(dividerLine());

  // metadata
  printer.println(padLine(" Rating", RATING));
  printer.println(padLine(" Fav", FAV_TRACK));
  String notesLine = String(" Notes: ") + String(NOTES);
  printer.println(notesLine);
  printer.println(dividerLine());

  printer.feed(3);
  printer.sleep();
}
