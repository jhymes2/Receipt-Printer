#ifndef RECEIPT_PRINT_H
#define RECEIPT_PRINT_H

#include <Arduino.h>
#include <HardwareSerial.h>
#include "Adafruit_Thermal.h"

#define LINE_WIDTH 32

void initPrinter();
void printReceipt();

#endif
