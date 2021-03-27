#ifndef __SERVO_CONFIG_H__
#define __SERVO_CONFIG_H__

#include "Defines.h"
#include "SendMessage.h"

#define CONFIG_COUNT 4

namespace ServoConfigurations {
  
  uint8_t servo_configurations[4][SERVO_COUNT] = {
    {0, 0, 0, 0, 0},                 // Zeros
    {0, 36, 72, 98, 134},          // Ascending
    {180, 134, 98, 72, 36},          // Descending
    {0, 180, 0, 180, 0}            // Alternating
  };

  /* Returns servo positions for a given configuration */
  uint8_t* GetConfiguration(int configuration) {
    if (configuration < 0 || configuration >= CONFIG_COUNT) {
      String str = String("Invalid servo configuration: ") + String(configuration) + String(" - setting to 0");
      Send::sendString(str);
      configuration = 0;
    }
    return servo_configurations[configuration];
  }
}

#endif
