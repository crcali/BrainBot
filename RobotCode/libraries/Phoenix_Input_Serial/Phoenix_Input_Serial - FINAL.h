//====================================================================
// [Include files]
#if ARDUINO>99
#include <Arduino.h> // Arduino 1.0
#else
#include <Wprogram.h> // Arduino 0022
#endif

//[CONSTANTS]
// Default to Serial but allow to be defined to something else
#ifndef SerSerial
#define SerSerial Serial
#endif

#ifndef SERIAL_BAUD
#define SERIAL_BAUD 38400
#endif

#define WALKMODE          0
#define TRANSLATEMODE     1
#define ROTATEMODE        2
#define SINGLELEGMODE     3
#define GPPLAYERMODE      4

#define SERB_PAD_LEFT    0x8000    //   bit7 - Left Button test
#define SERB_PAD_DOWN    0x4000    //   bit6 - Down Button test
#define SERB_PAD_RIGHT   0x2000    //   bit5 - Right Button test
#define SERB_PAD_UP      0x1000    //   bit4 - Up Button test
#define SERB_START       0x800      //   bit3 - Start Button test
#define SERB_R3          0x400    //   bit2 - R3 Button test (Horn)
#define SERB_L3          0x200    //   bit1 - L3 Button test
#define SERB_SELECT      0x100    //   bit0 - Select Button test
// DualShock(2)
#define SERB_SQUARE      0x80    //	bit7 - Square Button test
#define SERB_CROSS       0x40    //	bit6 - Cross Button test
#define SERB_CIRCLE      0x20    //	bit5 - Circle Button test
#define SERB_TRIANGLE    0x10    //	bit4 - Triangle Button test
#define SERB_R1          0x8    //	bit3 - R1 Button test
#define SERB_L1          0x4    //	bit2 - L1 Button test
#define SERB_R2          0x2    //	bit1 - R2 Button test
#define SERB_L2          0x1    //	bit0 - L2 Button test

#define  SER_RX          3             // DualShock(3) - Right stick Left/right
#define  SER_RY          4            // DualShock(4) - Right Stick Up/Down
#define  SER_LX          5            // DualShock(5) - Left Stick Left/right
#define  SER_LY          6            // DualShock(6) - Left Stick Up/Down


#define cTravelDeadZone 4      //The deadzone for the analog input from the remote
#define  MAXPS2ERRORCNT  5     // How many times through the loop will we go before shutting off robot?

#ifndef MAX_BODY_Y
#define MAX_BODY_Y 100
#endif

//=============================================================================
// Global - Local to this file only...
//=============================================================================

// Define an instance of the Input Controller...
InputController  g_InputController;       // Our Input controller 

static short       g_BodyYOffset; 
static word        g_wSerialErrorCnt;
static short       g_BodyYShift;
static byte        ControlMode;
static word        g_wButtonsPrev;
static bool        DoubleHeightOn;
static bool        DoubleTravelOn;
static bool        WalkMethod;
byte               GPSeq;             //Number of the sequence
short              g_sGPSMController;    // What GPSM value have we calculated. 0xff - Not used yet

bool run = false;
int k = 255;
int j = 255;

// some external or forward function references.
extern void SerTurnRobotOff(void);

// If both PS2 and XBee are defined then we will become secondary to the xbee
void InputController::Init(void)
{
  int error;
  


  // May need to init the Serial port here...
  SerSerial.begin(SERIAL_BAUD);
  
  g_BodyYOffset = 0;    
  g_BodyYShift = 0;
  g_wSerialErrorCnt = 0;  // error count

  ControlMode = WALKMODE;
  DoubleHeightOn = false;
  DoubleTravelOn = false;
  WalkMethod = false;

  g_InControlState.SpeedControl = 100;    // Sort of migrate stuff in from Devon.
}

//==============================================================================
// This function is called by the main code to tell us when it is about to
// do a lot of bit-bang outputs and it would like us to minimize any interrupts
// that we do while it is active...
//==============================================================================
void InputController::AllowControllerInterrupts(boolean fAllow)
{
  // We don't need to do anything...
  
}

#define ButtonPressed(wMask) (((wButtons & wMask) == 0) && ((g_wButtonsPrev & wMask) != 0))

//=====================================================================================
// This is The main code to input function to read inputs from the Serial port and then
//process any commands.
//=====================================================================================
void InputController::ControlInput(void)
{
  byte abDualShock[7];  
  unsigned long ulLastChar;
  boolean fAdjustLegPositions = false;
  word wButtons;

  char input; 

  input = SerSerial.read();

  // In an analog mode so should be OK...
  g_wSerialErrorCnt = 0;    // clear out error count...

  if (input == 's' || input == 'S') {
    if (g_InControlState.fRobotOn) {
      SerSerial.print("Off.");
      SerTurnRobotOff();
    } 
    else {
      //Turn on
      SerSerial.print("Started.");
      g_InControlState.fRobotOn = 1;
      fAdjustLegPositions = true;
    }
  }

  //Set to defult positions
  if (input == 'q' || input == 'Q') {
    SerSerial.print("Reset positions.");
    g_InControlState.TravelLength.z = (0);
    g_InControlState.TravelLength.x = (0);
    g_InControlState.TravelLength.y = (0);
    fAdjustLegPositions = true;
  }

  // Increase speed
  if  (input == 'u' || input == 'U') {
      if (g_InControlState.SpeedControl>0) {
        g_InControlState.SpeedControl = g_InControlState.SpeedControl - 50;
        MSound( 1, 50, 2000);  
        SerSerial.print("Increased speed.");
      }
    }

  //Decrease speed
  if (input == 'n' || input == 'N') {
    if (g_InControlState.SpeedControl<2000 ) {
      g_InControlState.SpeedControl = g_InControlState.SpeedControl + 50;
      MSound( 1, 50, 2000); 
      SerSerial.print("Decreased speed.");
    }
  }

  // Raise robot
  if (input == 'h' || input == 'H') {
    g_BodyYOffset += 10;
    SerSerial.print("Height up.");

      // And see if the legs should adjust...
      fAdjustLegPositions = true;
      if (g_BodyYOffset > MAX_BODY_Y)
        g_BodyYOffset = MAX_BODY_Y;
  }

  //Lower robot
  if (input == 'd' || input == 'D') {
    g_BodyYOffset -= 10;
    SerSerial.print("Height down.");
    // And see if the legs should adjust...
    fAdjustLegPositions = true;
    if (g_BodyYOffset > MAX_BODY_Y)
      g_BodyYOffset = MAX_BODY_Y;
  }
  
  //Circle
  if (input == 'c' || input == 'C') { // R3 Button Test
    SerSerial.print("Moving in a circle.");
    MSound(1, 50, 2000); 
    SerSerial.print(WalkMethod);
    g_InControlState.TravelLength.z = (255 - 128);
    g_InControlState.TravelLength.x = -1*(255 - 128);
    if (!DoubleTravelOn) {  //(Double travel length)
      g_InControlState.TravelLength.x = g_InControlState.TravelLength.x/2;
      g_InControlState.TravelLength.z = g_InControlState.TravelLength.z/2;
    } 
    g_InControlState.TravelLength.y = -(k - 128)/4; //Right Stick Left/Right 
  }

  //Double Travel Length
  if (input == 'o' || input == 'O') {// R2 Button Test
    SerSerial.print("DoubleTravelLength.");
    MSound(1, 50, 2000); 
    DoubleTravelOn = !DoubleTravelOn;
  }

  //Double leg lift height
  if (input == 'M' || input == 'm') { // R1 Button Test
    SerSerial.print("DoubleLegHeight");
    MSound( 1, 50, 2000); 
    DoubleHeightOn = !DoubleHeightOn;
    if (DoubleHeightOn) {
      SerSerial.print("LegLiftHeight Increased");
      g_InControlState.LegLiftHeight = 80;
    }
    else {
      SerSerial.print("LegLiftHeight Increased");
      g_InControlState.LegLiftHeight = 50;
    }
  }

  //Move diagonal 
  if (input == 'i' || input == 'I') { 
    SerSerial.print(WalkMethod);
    SerSerial.print("Moving diagonal");
    g_InControlState.TravelLength.z = (255 - 128);
    g_InControlState.TravelLength.x = (255 - 128);

    if (!DoubleTravelOn) {  //(Double travel length)
      g_InControlState.TravelLength.x = g_InControlState.TravelLength.x/2;
      g_InControlState.TravelLength.z = g_InControlState.TravelLength.z/2;
    } 


    g_InControlState.TravelLength.y = -(k - 128)/4; //Right Stick Left/Right 
  }

  //Move straight
  if (input == 'f' || input == 'F') {
    SerSerial.print("Moving forward");
    g_InControlState.TravelLength.z = (255-128); 
  }

  //Move backward
  if (input == 'b' || input == 'B') {
    SerSerial.print("Moving backward");
    g_InControlState.TravelLength.z = (-1*(255-128));   
  } 

  //Move left
  if (input == 'L' || input == 'l') {
    SerSerial.print("Moving Left");
    g_InControlState.TravelLength.x = (225-128); 
  }

  //Rotate in place
  if (input == 'p' || input == 'P') {
    SerSerial.print("Rotating in place.");
    g_InControlState.TravelLength.y = (128)/4;
  }

  //Switch gates
  if (input == 'g' || input == 'G') {
    g_InControlState.GaitType = g_InControlState.GaitType+1; 
    if (g_InControlState.GaitType<NUM_GAITS) {                 // Make sure we did not exceed number of gaits...
      MSound( 1, 50, 2000); 
      SerSerial.print("Gait:");
      SerSerial.print(g_InControlState.GaitType);
      SerSerial.print(".");
    } 
    else {
      MSound(2, 50, 2000, 50, 2250); 
      g_InControlState.GaitType = 0;
    }
    GaitSelect();
  }

  //Translate mode
  if (input == 't' || input == 'T') {
    SerSerial.print("Translate Mode.")
    g_InControlState.BodyPos.x = (255 - 128)/2;
    g_InControlState.BodyPos.z = -(255 - 128)/3;
    g_InControlState.BodyRot1.y = (255 - 128)*2;
    g_BodyYShift = (-(255 - 128)/2);
    
    g_InControlState.BodyPos.x = ( 255 )/2;
    g_InControlState.BodyPos.z = -( 255 )/3;
    g_InControlState.BodyRot1.y = ( 255 )*2;
    g_BodyYShift = (-( 255 )/2);


    }

  //Rotate mode
  if (input == 'r' || input == 'R') {
    SerSerial.print("Rotate Mode.");
    g_InControlState.BodyRot1.x = (255 - 128);
    g_InControlState.BodyRot1.y = (255 - 128)*2;
    g_InControlState.BodyRot1.z = (255 - 128);
    g_BodyYShift = (-(255 - 128)/2);
  }

  if (run) {

#ifdef OPT_GPPLAYER
    // GP Player Mode X
    if (ButtonPressed(SERB_CROSS)) { // X - Cross Button Test
      MSound(1, 50, 2000);  
      if (ControlMode != GPPLAYERMODE) {
        ControlMode = GPPLAYERMODE;
        GPSeq=0;
      } 
      else
        ControlMode = WALKMODE;
    }
#endif // OPT_GPPLAYER

    //[Common functions]
    //Switch Balance mode on/off 
    if (ButtonPressed(SERB_SQUARE)) { // Square Button Test
      g_InControlState.BalanceMode = !g_InControlState.BalanceMode;
      if (g_InControlState.BalanceMode) {
        MSound(1, 250, 1500); 
      } 
      else {
        MSound( 2, 100, 2000, 50, 4000);
      }
    }

    //Stand up, sit down  
    if (ButtonPressed(SERB_TRIANGLE)) { // Triangle - Button Test
      if (g_BodyYOffset>0) 
        g_BodyYOffset = 0;
      else
        g_BodyYOffset = 35;
      fAdjustLegPositions = true;
    }

    if (ButtonPressed(SERB_PAD_UP)) {// D-Up - Button Test
      g_BodyYOffset += 10;

      // And see if the legs should adjust...
      fAdjustLegPositions = true;
      if (g_BodyYOffset > MAX_BODY_Y)
        g_BodyYOffset = MAX_BODY_Y;
    }

    if (ButtonPressed(SERB_PAD_DOWN) && g_BodyYOffset) {// D-Down - Button Test
      if (g_BodyYOffset > 10)
        g_BodyYOffset -= 10;
      else
        g_BodyYOffset = 0;      // constrain don't go less than zero.

      // And see if the legs should adjust...
      fAdjustLegPositions = true;
    }

    

    //[Walk functions]
    if (ControlMode == WALKMODE) {
      //Switch gates
      if (ButtonPressed(SERB_SELECT)            // Select Button Test
      && abs(g_InControlState.TravelLength.x)<cTravelDeadZone //No movement
      && abs(g_InControlState.TravelLength.z)<cTravelDeadZone 
        && abs(g_InControlState.TravelLength.y*2)<cTravelDeadZone  ) {
        g_InControlState.GaitType = g_InControlState.GaitType+1;                    // Go to the next gait...
        if (g_InControlState.GaitType<NUM_GAITS) {                 // Make sure we did not exceed number of gaits...
          MSound( 1, 50, 2000); 
        } 
        else {
          MSound(2, 50, 2000, 50, 2250); 
          g_InControlState.GaitType = 0;
        }
        GaitSelect();
      }

      //Double leg lift height
      if (ButtonPressed(SERB_R1)) { // R1 Button Test
        MSound( 1, 50, 2000); 
        DoubleHeightOn = !DoubleHeightOn;
        if (DoubleHeightOn)
          g_InControlState.LegLiftHeight = 80;
        else
          g_InControlState.LegLiftHeight = 50;
      }

      //Double Travel Length
      if (ButtonPressed(SERB_R2)) {// R2 Button Test
        MSound(1, 50, 2000); 
        DoubleTravelOn = !DoubleTravelOn;
      }

      // Switch between Walk method 1 && Walk method 2
      if (ButtonPressed(SERB_R3)) { // R3 Button Test
        MSound(1, 50, 2000); 
        WalkMethod = !WalkMethod;
      }

      //Walking
      if (WalkMethod)  //(Walk Methode) 
        g_InControlState.TravelLength.z = (abDualShock[SER_RY]-128); //Right Stick Up/Down  

      else {
        g_InControlState.TravelLength.x = -(abDualShock[SER_LX] - 128);
        g_InControlState.TravelLength.z = (abDualShock[SER_LY] - 128);
      }

      if (!DoubleTravelOn) {  //(Double travel length)
        g_InControlState.TravelLength.x = g_InControlState.TravelLength.x/2;
        g_InControlState.TravelLength.z = g_InControlState.TravelLength.z/2;
      }

      g_InControlState.TravelLength.y = -(abDualShock[SER_RX] - 128)/4; //Right Stick Left/Right 
    }

    //[Translate functions]
    g_BodyYShift = 0;
    if (ControlMode == TRANSLATEMODE) {
      g_InControlState.BodyPos.x = (abDualShock[SER_LX] - 128)/2;
      g_InControlState.BodyPos.z = -(abDualShock[SER_LY] - 128)/3;
      g_InControlState.BodyRot1.y = (abDualShock[SER_RX] - 128)*2;
      g_BodyYShift = (-(abDualShock[SER_RY] - 128)/2);
    }

    //[Rotate functions]
    if (ControlMode == ROTATEMODE) {
      g_InControlState.BodyRot1.x = (abDualShock[SER_LY] - 128);
      g_InControlState.BodyRot1.y = (abDualShock[SER_RX] - 128)*2;
      g_InControlState.BodyRot1.z = (abDualShock[SER_LX] - 128);
      g_BodyYShift = (-(abDualShock[SER_RY] - 128)/2);
    }

    //[Single leg functions]
    if (ControlMode == SINGLELEGMODE) {
      //Switch leg for single leg control
      if (ButtonPressed(SERB_SELECT)) { // Select Button Test
        MSound(1, 50, 2000); 
        if (g_InControlState.SelectedLeg< (CNT_LEGS-1))
          g_InControlState.SelectedLeg = g_InControlState.SelectedLeg+1;
        else
          g_InControlState.SelectedLeg=0;
      }

      g_InControlState.SLLeg.x= (abDualShock[SER_LX] - 128)/2; //Left Stick Right/Left
      g_InControlState.SLLeg.y= (abDualShock[SER_RY] - 128)/10; //Right Stick Up/Down
      g_InControlState.SLLeg.z = (abDualShock[SER_LY] - 128)/2; //Left Stick Up/Down

      // Hold single leg in place
      if (ButtonPressed(SERB_R2)) { // R2 Button Test
        MSound(1, 50, 2000);  
        g_InControlState.fSLHold = !g_InControlState.fSLHold;
      }
    }

#ifdef OPT_GPPLAYER
      //[GPPlayer functions]
      if (ControlMode == GPPLAYERMODE) {

        // Lets try some speed control... Map all values if we have mapped some before
        // or start mapping if we exceed some minimum delta from center
        // Have to keep reminding myself that commander library already subtracted 128...
        if (g_ServoDriver.FIsGPSeqActive() ) {
          if ((g_sGPSMController != 32767)  
            || (abDualShock[SER_RY] > (128+16)) || (abDualShock[SER_RY] < (128-16)))
          {
            // We are in speed modify mode...
            short sNewGPSM = map(abDualShock[SER_RY], 0, 255, -200, 200);
            if (sNewGPSM != g_sGPSMController) {
              g_sGPSMController = sNewGPSM;
              g_ServoDriver.GPSetSpeedMultiplyer(g_sGPSMController);
            }

          }
        }

        //Switch between sequences
        if (ButtonPressed(SERB_SELECT)) { // Select Button Test
          if (!g_ServoDriver.FIsGPSeqActive() ) {
            if (GPSeq < 5) {  //Max sequence
              MSound(1, 50, 1500);
              GPSeq = GPSeq+1;
            } 
            else {
              MSound(2, 50, 2000, 50, 2250);
              GPSeq=0;
            }
          }
        }
        //Start Sequence
        if (ButtonPressed(SERB_R2))// R2 Button Test
          if (!g_ServoDriver.FIsGPSeqActive() ) {
            g_ServoDriver.GPStartSeq(GPSeq);
            g_sGPSMController = 32767;  // Say that we are not in Speed modify mode yet... valid ranges are 50-200 (both postive and negative... 
          }
          else {
            g_ServoDriver.GPStartSeq(0xff);    // tell the GP system to abort if possible...
            MSound (2, 50, 2000, 50, 2000);
          }


      }
#endif // OPT_GPPLAYER

      //Calculate walking time delay
      g_InControlState.InputTimeDelay = 128 - max(max(abs(abDualShock[SER_LX] - 128), abs(abDualShock[SER_LY] - 128)), abs(abDualShock[SER_RX] - 128));
    }

    //Calculate g_InControlState.BodyPos.y
    g_InControlState.BodyPos.y = min(max(g_BodyYOffset + g_BodyYShift,  0), MAX_BODY_Y);
    if (fAdjustLegPositions)
      AdjustLegPositionsToBodyHeight();    // Put main workings into main program file

  // remember which buttons were set here
  g_wButtonsPrev = wButtons; 
}

//==============================================================================
// SerTurnRobotOff - code used couple of places so save a little room...
//==============================================================================
void SerTurnRobotOff(void)
{
  //Turn off
  g_InControlState.BodyPos.x = 0;
  g_InControlState.BodyPos.y = 0;
  g_InControlState.BodyPos.z = 0;
  g_InControlState.BodyRot1.x = 0;
  g_InControlState.BodyRot1.y = 0;
  g_InControlState.BodyRot1.z = 0;
  g_InControlState.TravelLength.x = 0;
  g_InControlState.TravelLength.z = 0;
  g_InControlState.TravelLength.y = 0;
  g_BodyYOffset = 0;
  g_BodyYShift = 0;
  g_InControlState.SelectedLeg = 255;
  g_InControlState.fRobotOn = 0;
  AdjustLegPositionsToBodyHeight();    // Put main workings into main program file
}






