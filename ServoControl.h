#ifndef __SERVO_CONTROL_H__
#define __SERVO_CONTROL_H__
#include "Defines.h"
#include <Servo.h>

namespace ServoControl {
  
  Servo finger0;
  Servo finger1;
  Servo finger2;
  Servo finger3;
  Servo thumb0;
  Servo thumb1;
  
  void init() {
    finger0.attach(FINGER_0_PIN);
    finger1.attach(FINGER_1_PIN);
    finger2.attach(FINGER_2_PIN);
    finger3.attach(FINGER_3_PIN);
    thumb0.attach(THUMB_0_PIN);
    thumb1.attach(THUMB_1_PIN);
  }

  void setServoPosition(uint8_t servo, uint8_t position) {
    switch(servo) {
      case 0: finger0.write(position); break;
      case 1: finger1.write(position); break;
      case 2: finger2.write(position); break;
      case 3: finger3.write(position); break;
      case 4: thumb0.write(position); break;
      case 5: thumb1.write(position); break;
    }
  }

  void setAllServoPositions(uint8_t* positions) {
    finger0.write(positions[0]);
    finger1.write(positions[1]);
    finger2.write(positions[2]);
    finger3.write(positions[3]);
    thumb0.write(positions[4]);
    thumb1.write(positions[5]);
  }

}
#endif
