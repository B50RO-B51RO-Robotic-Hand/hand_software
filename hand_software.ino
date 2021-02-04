#include "ServoControl.h"

void setup() {
  Serial.begin(9600);
  ServoControl::init();
}

void loop() {
  // Check for messages
  if (Serial.available()) {
    uint8_t in = Serial.read();

    /*
     * Message format is as follows
     *                            Byte 0
     * Individual servo control : 0000 0 [3:motor selection, 000-101]  [8:motor position]
     * Pre-set configuration    : 1 [7:configuration]
     * 
     * TODO: Decide how many configurations to allow - message format allows up to 128
     */
    
    if ((in >> 3) == 0) {         // Individual servo control
      // Servo to control is number 0 to 5
      // 0: finger 0
      // 1: finger 1
      // 2: finger 2
      // 3: finger 3
      // 4: thumb  0
      // 5: thumb  1
      uint8_t servo = in;         // First 5 bits are 0, so last 3 bits correspond to servo
      if (servo > 5) {            // Invalid servo selected!
        Serial.print("Error: invalid servo selected : ");
        Serial.println(servo);
      }
      // Read desired servo position from next byte
      uint8_t position = Serial.read();
      // Move servo to desired position
      ServoControl::setServoPosition(servo, position);
    } else if ((in >> 7) == 1) {  // Set servos to preset position
      // TODO: create default positions and set servos
      // Can use ServoControl::setAllServoPositions(int[]);
      Serial.print("Not implemented - config preset ");
      Serial.println((in - 0b10000000));
    } else {
      Serial.print("Error: invalid command received : ")
      Serial.println(in, BIN);
    }
  }
}
