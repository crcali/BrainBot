
//=============================================================================
// Header Files
//=============================================================================

#define DEFINE_HEX_GLOBALS
#if ARDUINO>99
#include <Arduino.h>
#else
#endif
#include <Wire.h>
#include <EEPROM.h>
#include <PS2X_lib.h>

#include <SoftwareSerial.h>
#include "Hex_Cfg.h"
#include <Phoenix.h>
//#include <diyxbee.h>
//#include <diyxbee_code.h>
#include <Phoenix_Input_DIYXbee.h>
#include <Phoenix_Driver_SSC32.h>
#include <Phoenix_Code.h>

