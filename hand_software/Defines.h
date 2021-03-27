#ifndef __DEFINES_H__
#define __DEFINES_H__

// Servo motor pin defines
// These correspond to pin D2 to D7
#define FINGER_0_PIN 5
#define FINGER_1_PIN 6
#define FINGER_2_PIN 7
#define FINGER_3_PIN 8
#define THUMB_PIN 9
#define FORCE_READING_PIN 19

#define SERVO_COUNT 5

// If defined servos will not be controlled - debug info will be sent over serial instead
#define DEBUG_ONLY

// If defined false force readings will be generated - used to test data graphing
#define GENERATE_FALSE_FORCE_DATA

#endif
