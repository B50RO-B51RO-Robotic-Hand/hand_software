#include "ServoControl.h"

void setup() {
  Serial.begin(9600);
  ServoControl::init();
}

void loop() {
  // Check for messages
  if (Serial.available()) {
    uint8_t in = Serial.read();
    if ((in >> 3) == 0) {   // Individual servo control
      
    }
  }
}
