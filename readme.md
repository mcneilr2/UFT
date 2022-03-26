# Universal Tensile Testing Machine Full-Stack Software

A full-stack software for control and automation of a universal tensile testing machine for the purpose of foam manufacturing materials characterization.  The firmware.ino module was uploaded to an arduino uno via the arduino ide with the HX711 library import (https://github.com/bogde/HX711.git) for the associated force cell amplifier board.  The actuator is a 12V bullet style actuator with a hall sensor to manage displacement.  **Instructables link to follow with complete hardware/electromechanical project details

The current version I am working on utilizes a local MySQL database with the following credentials:

```
 conn = mysql.connector.connect(host = 'localhost', user = 'root', passwd = 'password', database = 'foam')
```

You can download and install MySQL from here: https://dev.mysql.com/downloads/ and edit the database credentials/columns and queries as needed.  The database population on tab2 and the record results option are all commented out in the code so the GUI can run without acces initially.

Currenty working on an sqlite version which will carry a localized database file in the file structure from computer to computer.  As we only have one machine at our shop, the database will only need to be accessed by one user at a time which means a localized database file can be moved from computer to computer as needed without the need to allow remote access through MySQL.  These are all sort of hacky fixes at this point, if you wanted to scale this project up, a cloud based database manager would be nessesary.

The purpose of the machine is to facilitate the testing of flexible polyurethane foams with the ability to customize testing standards from ASTM D3574-17.

# Installation and Execution

# Usage

