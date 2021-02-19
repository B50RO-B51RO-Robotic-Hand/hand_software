#ifndef __SERVO_CONTROL_H__
#define __SERVO_CONTROL_H__

#include "Defines.h"

#include <Servo.h>

namespace ServoControl {

  // Declarations
  void setServoPosition(uint8_t servo, uint8_t position);
  void setAllServoPositions(uint8_t* positions);

  Servo servos[6];
  uint8_t servo_limits[] = {
                        0, 255, // Servo 0
                        0, 255, // Servo 1
                        0, 255, // Servo 2
                        0, 255, // Servo 3
                        0, 255, // Servo 4
                        0, 255  // Servo 5
                       };
  uint8_t servo_positions[] = {
    0, 0, 0, 0, 0, 0            // Servos 0 -> 5
  };

  /* Initialise servo motors */
  void init() {
    
    #ifndef DEBUG_ONLY
    
    servos[0].attach(FINGER_0_PIN);
    servos[1].attach(FINGER_1_PIN);
    servos[2].attach(FINGER_2_PIN);
    servos[3].attach(FINGER_3_PIN);
    servos[4].attach(THUMB_0_PIN);
    servos[5].attach(THUMB_1_PIN);
    
    #endif

    uint8_t zeros[] = {0, 0, 0, 0, 0, 0};
    setAllServoPositions(zeros);
    
  }

  /* Set the position of a single servo */
  void setServoPosition(uint8_t servo, uint8_t position) {
    // Ensure position is within required limits
    if (position < servo_limits[2*servo])
      position = servo_limits[2*servo];
    else if (position > servo_limits[2*servo+1])
      position = servo_limits[2*servo+1];
    
    #ifndef DEBUG_ONLY
    
    servos[servo].write(position);
    
    #else
    
    Serial.print("Servo ");
    Serial.print(servo);
    Serial.print(" set to ");
    Serial.println(position);
    
    #endif

    servo_positions[servo] = position;
  }

  /* Set the position of all servos
   *  positions must be a 6-element array
   */
  void setAllServoPositions(uint8_t* positions) {
    // Limit positions
    // Note - this may change the config values in memory
    //    This should not matter unless limits are to be changed on the fly
    for (uint8_t i = 0; i < 6; i++) {
      if (positions[i] < servo_limits[i*2])
        positions[i] = servo_limits[i*2];
      else if (positions[i] > servo_limits[i*2+1])
        positions[i] = servo_limits[i*2+1];
    }
    
    #ifndef DEBUG_ONLY
    
    for (uint8_t i = 0; i < 6; i++) {
      servos[i].write(positions[i]);
      servo_positions[i] = positions[i];
    }
    
    #else
    
    Serial.print("Servo positions set as follows: ");
    for (uint8_t i = 0; i < 6; i++) {
      Serial.print(positions[i]);
      Serial.print(" ");
      servo_positions[i] = positions[i];
    }
    Serial.println("");
    
    #endif
  }

  /* Send current requested servo position details */
  void sendPositionDetails() {
    Serial.print("Servo positions: ");
    for (uint8_t i = 0; i < 6; i++) {
      #ifndef DEBUG_ONLY
      Serial.print(servos[i].read());
      Serial.print('|');
      #endif
      Serial.print(servo_positions[i]);
      Serial.print(" ");
    }
    Serial.println("");
  }

  /* Send servo limits */
  void sendLimitDetails() {
    Serial.print("Servo limits: ");
    for (uint8_t i = 0; i < 6; i++) {
      Serial.print(servo_limits[2*i]);
      Serial.print(",");
      Serial.print(servo_limits[2*i + 1]);
      Serial.print(" ");
    }
    Serial.println("");
  }

}
#endif
