#ifndef __SERVO_CONFIG_H__
#define __SERVO_CONFIG_H__

#define CONFIG_COUNT 4

namespace ServoConfigurations {
  
  uint8_t servo_configurations[4][6] = {
    {0, 0, 0, 0, 0, 0},                 // Zeros
    {0, 51, 102, 153, 204, 255},        // Ascending
    {255, 204, 153, 102, 51, 0},        // Descending
    {0, 255, 0, 255, 0, 255}            // Alternating
  };

  /* Returns servo positions for a given configuration */
  uint8_t* GetConfiguration(int configuration) {
    if (configuration < 0 || configuration >= CONFIG_COUNT) {
      Serial.print("Invalid servo configuration: ");
      Serial.print(configuration);
      Serial.println(" - setting to 0");
      configuration = 0;
    }
    return servo_configurations[configuration];
  }
}

#endif
