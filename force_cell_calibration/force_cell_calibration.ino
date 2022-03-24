//Read Force Arduino Program

#include "HX711.h"

float calibration_factor = -4400;

const int LOADCELL_DOUT_PIN = 4;
const int LOADCELL_SCK_PIN = 5;

HX711 scale;

char operation; // Holds operation (R, W, ...)
char mode; // Holds the mode (D, A)
int pin_number; // Holds the pin number
int value_to_write; // Holds the value that we want to write
float speedvalue;
int wait_for_transmission = 5; // Delay in ms in order to receive the serial data
float conNum = ((0.000286/5*25.4)*7.6);
unsigned long lastStepTime = 0;  //time stamp of last pulse
int trigDelay = 500;  //delay between pulse microseconds
unsigned long prevTimer = 0;  //previous time stamp
long pos = 0;
float travelled = 0;
long steps = 0;
int extend = 11;
int retract = 10;
bool homeFlag = 0;
long prevSteps = 0;
float average = 0;

void calib(float spring){
  scale.tare();
    
    do{
      analogWrite(10, 0);
      analogWrite(11, 20);
    }while(scale.get_units() < 0.5);
    analogWrite(10, 0);
    analogWrite(11, 0);
  delay(1000);
  steps = 0;
  travelled = 0;
  pos = 0;
    do{
      analogWrite(10, 0);
      analogWrite(11, 50);
      if(millis() - prevTimer > 100){  //update every 1/10 of a second
        pos = pos + steps;
        travelled = conNum * pos;
        steps = 0;
        prevTimer = millis();
      }
    }while(travelled <= 40.5);
    analogWrite(10, 0);
    analogWrite(11, 0);

    do{
      scale.set_scale(calibration_factor);
      Serial.print("\nforce read: ");
      Serial.print(scale.get_units());
      Serial.print("\ncalib read: ");
      Serial.print(calibration_factor);
      if (scale.get_units(5) < 100){calibration_factor += 20;}
      else if (scale.get_units(5) > 102) {calibration_factor -= 20;}
    }while ((scale.get_units()<100) || (scale.get_units()>102));

    Serial.print("\nfinal calib: ");
    Serial.print(calibration_factor);
  }



void setup() {
    Serial.begin(9600); // Serial Port at 9600 baud
    pinMode(10, OUTPUT);
    pinMode(11, OUTPUT);
    pinMode(2, INPUT);
    attachInterrupt(digitalPinToInterrupt(2), countSteps, RISING);
    scale.begin(LOADCELL_DOUT_PIN, LOADCELL_SCK_PIN);
    scale.set_scale(calibration_factor);
}

void loop() {
    // Check if characters available in the buffer
    if (Serial.available() > 0) {
        operation = Serial.read();
        delay(wait_for_transmission); // If not delayed, second character is not correctly read
        mode = Serial.read();
        pin_number = Serial.parseInt(); // Waits for an int to be transmitted
        if (Serial.read()==':'){
            value_to_write = Serial.parseFloat(); // Collects the value to be written
        }
        switch (operation){
            case 'W': // Write operation, e.g. WD3:1, WA8:255
                if (mode == 'C'){
                    calib(value_to_write);
                } else {
                    break; // Unexpected mode
                }
                break;
            default: // Unexpected char
                break;
        }
    }
}
