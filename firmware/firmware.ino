//Read Force Arduino Program

#include "HX711.h"

float calibration_factor = -4400;

const int LOADCELL_DOUT_PIN = 4;
const int LOADCELL_SCK_PIN = 5;

HX711 scale;

char operation; // Holds operation (R, W, ...)
char mode; // Holds the mode (D, A)
int pin_number; // Holds the pin number
int digital_value; // Holds the digital value
int analog_value; // Holds the analog value
int value_to_write; // Holds the value that we want to write
float speedvalue;
int wait_for_transmission = 5; // Delay in ms in order to receive the serial data
float conNum = ((0.000286/5*25.4)*7.6);
float fullspeed = 255;
float halfspeed = 127;
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
int default_pausetime = 5000;
int default_forcestop = 2;

void tare_read(){
  scale.tare();
  Serial.print(scale.get_offset()); 
}

void read_force(float offset){
  scale.set_offset(offset);
  Serial.print(scale.get_units()); 
}

void homeActuator(void){
  int count = 0;
  prevTimer = millis();
  while(homeFlag == 0){
    analogWrite(extend,0);
    analogWrite(retract, fullspeed);
    if(prevSteps == steps){
      if(millis() - prevTimer > 100){
        analogWrite(extend, 0);
        analogWrite(retract, 0);
        steps = 0;
        homeFlag = 1;
      }
    }
    else{
      prevSteps = steps;
      prevTimer = millis();
    }
  }
    do{
  Serial.print("1");
  count++;
  }while(count < 10);
}
void go_the_distance(int pin_number, float mm, float speedvalue){

  steps = 0;
  travelled = 0;
  pos = 0;
  int count = 0;

  
  if (pin_number == 10){
    do{
      analogWrite(10, speedvalue);
      analogWrite(11, 0);
      if(millis() - prevTimer > 100){  //update every 1/10 of a second
        pos = pos + steps;
        travelled = conNum * pos;
        steps = 0;
        prevTimer = millis();
      }
    }while(travelled <= mm);
    analogWrite(10, 0);
    analogWrite(11, 0);
    
  }
  else if (pin_number == 11){
    do{
      analogWrite(10, 0);
      analogWrite(11, speedvalue);
      if(millis() - prevTimer > 100){  //update every 1/10 of a second
        pos = pos + steps;
        travelled = conNum * pos;
        steps = 0;
        prevTimer = millis();
      }
    }while(travelled <= mm);
    analogWrite(10, 0);
    analogWrite(11, 0);
  }
  do{
  Serial.print("1");
  count++;
  }while(count < 10);
 
}

void force_stop(float threshold, float two_five_distance){
  scale.tare();
  steps = 0;
  travelled = 0;
  pos = 0;
  prevTimer = 0;
  int count = 0;
//  
    do{
      analogWrite(10, 0);
      analogWrite(11, 20);
    }while(scale.get_units() < threshold);
    analogWrite(10, 0);
    analogWrite(11, 0);
//    
    
    delay(2000);
    go_the_distance(extend,two_five_distance,65);
    delay(5000);
    
}



void stop_now(void){
  Serial.print("stp\n");
}

void countSteps(void){
  if(micros() - lastStepTime > trigDelay){
    steps++;
    lastStepTime = micros();
  }
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
        if (Serial.read()==':'){
            speedvalue = Serial.parseFloat(); // Collects the value to be written
        }
        switch (operation){
            case 'W': // Write operation, e.g. WD3:1, WA8:255
                if (mode == 'G'){
                    go_the_distance(pin_number, value_to_write, speedvalue);
                } else if (mode == 'F'){
                    force_stop(value_to_write, speedvalue);
                } else if (mode == 'H'){
                    homeActuator();
                } else {
                    break; // Unexpected mode
                }
                break;
             case 'R':
                if (mode == 'F'){
                    read_force(value_to_write);
                } else if (mode == 'T'){
                    tare_read();                   
                } else  {
                  break;
                }
                break;
            default: // Unexpected char
                break;
        }
    }
}
