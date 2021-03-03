#ifndef __SENSOR_READING_H__
#define __SENSOR_READING_H__

#include "SendMessage.h"

namespace Sensor {

  uint32_t rawForceTimestamp = 0;
  uint8_t rawForceReading = 0;

  void updateReading() {
    rawForceTimestamp = millis();

    // Create false readings for testing purposes
    float modifiedTime = (float) rawForceTimestamp / 1000.0;
    float reading = sin(modifiedTime) * 128 + 128;
    rawForceReading = (uint8_t) reading;
  }

  void sendReadingDetails() {
    Send::sendRawForce(rawForceTimestamp, rawForceReading);
  }
  
}

#endif
