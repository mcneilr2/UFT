# Universal Tensile Testing Machine Full-Stack Software

A full-stack software for control and automation of a universal tensile testing machine for the purpose of foam manufacturing materials characterization.  The firmware.ino module was uploaded to an arduino uno via the arduino ide with the HX711 library import (https://github.com/bogde/HX711.git) for the associated force cell amplifier board.  The actuator is a 12V bullet style actuator with a hall sensor to manage displacement.  **Instructables link to follow with complete hardware/electromechanical project details

The current version I am working on utilizes a local MySQL database with the following credentials:

'''
 conn = mysql.connector.connect(host = 'localhost', user = 'root', passwd = 'password', database = 'foam')
 '''

# Table of Contents


# Installation and Execution

# Usage

