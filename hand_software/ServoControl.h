#ifndef __SERVO_CONTROL_H__
#define __SERVO_CONTROL_H__

#include "Defines.h"
#include "SendMessage.h"

#include <Servo.h>

namespace ServoControl {

  // Declarations
  void setServoPosition(uint8_t servo, uint8_t position);
  void setAllServoPositions(uint8_t* positions);

  Servo servos[6];
  uint8_t servo_limits[] = {
                        0, 180, // Servo 0
                        0, 180, // Servo 1
                        0, 180, // Servo 2
                        0, 180, // Servo 3
                        0, 180, // Servo 4
                        0, 180  // Servo 5
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
    setAllServoPositions(zeros);              // Initially set all servos to 0 position
    
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

    String msg = String("Servo ") + String(servo) + String(" set to ") + String(position);
    Send::sendString(msg);
    
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

    String msg = "Servo positions set as follows: ";
    
    for (uint8_t i = 0; i < 6; i++) {
      msg += String(positions[i]);
      msg += " ";
      servo_positions[i] = positions[i];
    }
    Send::sendString(msg);
    
    #endif
  }

  /* Send current requested servo position details */
  void sendPositionDetails() {
    Send::sendAllServoPositions(servo_positions);
  }

  /* Send servo limits */
  void sendLimitDetails() {
    Send::sendAllServoLimits(servo_limits);
  }

}
#endif
