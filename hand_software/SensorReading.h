#ifndef __SENSOR_READING_H__
#define __SENSOR_READING_H__

#include "SendMessage.h"

namespace Sensor {

  uint32_t rawForceTimestamp = 0;
  uint16_t rawForceReading = 0;

  void updateReading() {
    rawForceTimestamp = millis();

    #ifdef GENERATE_FALSE_FORCE_DATA
  
    // Create false readings for testing purposes
    float modifiedTime = (float) rawForceTimestamp / 1000.0;
    float reading = sin(modifiedTime) * 512 + 512;
    rawForceReading = (uint16_t) reading;

    #else

    // ADC pins have a resolution of 10 bits -> range of 0 to 1023
    // uint16_t used to read value
    rawForceReading = analogRead(FORCE_READING_PIN);

    #endif
    
  }

  void sendReadingDetails() {
    Send::sendRawForce(rawForceTimestamp, rawForceReading);
  }
  
}

#endif
