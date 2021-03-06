#include "ServoControl.h"
#include "ServoConfig.h"
#include "SendMessage.h"
#include "SensorReading.h"

#define QUERY_ALL_POSITIONS 0b00001000
#define QUERY_ALL_LIMITS 0b00001001
#define QUERY_FORCE_RAW 0b00001010
#define TOGGLE_FORCE_STREAM 0b00001011

void setup() {
  Serial.begin(9600);
  ServoControl::init();
}

bool sendForceStream = false;

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
    
    if ((in >> 3) == 0b00000) {   // Individual servo control
      // Servo to control is number 0 to 5
      // 0: finger 0
      // 1: finger 1
      // 2: finger 2
      // 3: finger 3
      // 4: thumb
      uint8_t servo = in;         // First 5 bits are 0, so last 3 bits correspond to servo
      if (servo > SERVO_COUNT - 1) {            // Invalid servo selected!
        String str = String("Error: invalid servo selected : ") + String(servo);
        Send::sendString(str);
      }
      // Read desired servo position from next byte
      while (!Serial.available());
      uint8_t position = Serial.read();
      // Move servo to desired position
      ServoControl::setServoPosition(servo, position);
    } else if (in == QUERY_ALL_POSITIONS) {   // Query all current positions
      ServoControl::sendPositionDetails();
    } else if (in == QUERY_ALL_LIMITS) {      // Query joint limits
      ServoControl::sendLimitDetails();
    } else if (in == QUERY_FORCE_RAW) {       // Query force reading
      Sensor::updateReading();      // Get new reading
      Sensor::sendReadingDetails(); // Send reading
    } else if (in == TOGGLE_FORCE_STREAM) {   // Toggle force reading data stream
      sendForceStream = !sendForceStream;
    } else if ((in >> 7) == 1) {              // Set servos to preset position
      // Retrieve configuration and set servos to it
      uint8_t *positions = ServoConfigurations::GetConfiguration(in - 0b10000000);
      ServoControl::setAllServoPositions(positions);
    } else {
      String str = String("Error: invalid command received : ") + String(in, BIN);
      Send::sendString(str);
    }
  }
  if (sendForceStream) {
    Sensor::updateReading();
    Sensor::sendReadingDetails();
    delay(100);
  }
}
