#ifndef __SEND_MESSAGE_H__
#define __SEND_MESSAGE_H__

#define MSG_CHAR_ARRAY_START 0b10000000
#define MSG_SERVO_POSITION_START 0b00000000
#define MSG_ALL_POSITIONS 0b00001000
#define MSG_ALL_LIMITS 0b00001001
#define MSG_FORCE_RAW 0b00001010

#define MAX_SINGLE_MESSAGE_LENGTH 128

namespace Send {

  // Send a single byte
  // Note - if there is no available buffer space this method will block until the byte is sent
  void sendMessageByte(uint8_t msg) {
    while (!Serial.availableForWrite());  // Wait for write to be available (note - will block)
    Serial.write(msg);
  }

  // Send a String message
  // Strings are sent in 128-character chunks
  // Length of String = (first_byte - MSG_CHAR_ARRAY_START) + 1
  //    e.g. 0b10000100 = 0b100 + 1 = 5 characters
  void sendString(String str) {
    char* chars = str.c_str();
    int len = str.length();
    int ind = 0;

    // Split the string into multiple messages if required
    while (len > MAX_SINGLE_MESSAGE_LENGTH) {
      sendMessageByte(MSG_CHAR_ARRAY_START | (MAX_SINGLE_MESSAGE_LENGTH - 1));
      len -= MAX_SINGLE_MESSAGE_LENGTH;
      for (int i = 0; i < MAX_SINGLE_MESSAGE_LENGTH; i++)
        sendMessageByte(chars[ind++]);
    }
    sendMessageByte(MSG_CHAR_ARRAY_START | (len - 1));
    for (int i = 0; i < len; i++)
        sendMessageByte(chars[ind++]);
  }

  // Individual servo position
  void sendServoPosition(uint8_t servo, uint8_t pos) {
    sendMessageByte(MSG_SERVO_POSITION_START + servo);
    sendMessageByte(pos);
  }

  // All servo positions
  void sendAllServoPositions(uint8_t* positions) {
    sendMessageByte(MSG_ALL_POSITIONS);
    for (int i=0; i<6; i++) {
      sendMessageByte(positions[i]);
    }
  }

  // All servo limits
  // Limits are in order as follows:
  // Servo 0 min,   Servo 0 max,   Servo 1 min,   Servo 1 max,   Servo 2 min,   Servo 2 max,
  // Servo 3 min,   Servo 3 max,   Servo 4 min,   Servo 4 max,   Servo 5 min,   Servo 5 max
  void sendAllServoLimits(uint8_t* limits) {
    sendMessageByte(MSG_ALL_LIMITS);
    for (int i=0; i<6*2; i++) {
      sendMessageByte(limits[i]);
    }
  }

  // Send a raw force reading
  void sendRawForce(uint8_t reading) {
    sendMessageByte(MSG_FORCE_RAW);
    sendMessageByte(reading);
  }

}

#endif
