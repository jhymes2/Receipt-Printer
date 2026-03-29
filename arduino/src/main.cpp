#include <Arduino.h>
#include "receipt_print.h"

void setup() {
  initPrinter();
  printReceipt();
}

void loop() {
  // intentionally empty — one-shot print on boot
}
