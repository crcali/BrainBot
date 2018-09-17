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

#include <SoftwareSerial.h>
#include "Hex_CFG.h"
#include <Phoenix.h>
#include <Phoenix_Input_Serial - FINAL.h>
#include <Phoenix_Driver_SSC32.h>
#include <Phoenix_Code.h>

