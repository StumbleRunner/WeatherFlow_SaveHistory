# WeatherFlow_SaveHistory
This is a set of scripts that allows Weather Flow users to capture their current and historical weather data into an SQL database.
It consists of three elements: the schema for the database (Weather-schema.sql), the script you run for capturing the backdata (Capture_Old_Observations.py), and the script that you run to continuously capture the new data (Concatenate_Observations.py). 

## Contents
**[Requirements](#requirements)**<br>
**[Installation Instructions](#installation-instructions)**<br>
**[Running the Script](#running-the-script)**<br>
**[More Advanced Topics](#more-advanced-topics)**<br>

## Requirements

* Python
  * this was written using Python 3 and it won't run in any version of Python 2.
  * having the python executable on your system search path is helpful but not strictly necessary.
* An SQL database containing the weather data
  * other database types should also work but would require script tweaks. 
  * I use MySQL because it's easy to come by, easy to configure, and free. 
  * You can grab a copy of the MySQL Community Server from here [Dev.MySQL.Com](https://dev.mysql.com/downloads/mysql/)
* Basic text file editing skills

These scripts are largely platform agnostic and should run on any machine capable of running python with the necessary libraries. The SQL database doesn't have to be local to the platform you're running the script on.


## Installation Instructions

These scripts don't need to be in any particular place on your system and they don't create any files but I prefer to keep them in their own directory for neatness reasons. It's assumed prior to following these instructions that you've installed MySQL or it's equivalent. 

1. Download the scripts and the schema

2. Open a command prompt and enter the following command:
```
python -m pip install --upgrade pip
```
If python isn't on your search path that line (and subsequent python references) may need to have the path to python pre-pended to the them.

3. Once that process has finished, run: 
```
python -m pip install pymysql json requests
```

4. Assuming you haven't already set up a weather database, you now want to load up the database schema as follows (this assumes you used root as the default user name, if not, then replace with the user name you chose):
```
mysql -u root --password < Weather-schema.sql
```

5. When that's done, go to the directory where you saved the python files and open both files in a text editor, the edits you'll need to make are same in each. Go to the section marked #device info and replace my device ID values with the ones specific for your weather station, which you can find by going to the settings page in the app or webpage, selecting Stations, pick your station and then Status. The device ID(s) are listed right there. Your API_Key is something you get by going to this page https://weatherflow.github.io/SmartWeather/api/ and selecting "Please contact us to obtain your own API key".
```
airDeviceID = "3781"
skyDeviceID = "10632"
API_Key = "apikey"
```

5. Next, go down to the next section marked #database info (about 23 lines in) and replace the default values with the ones specific for your database. 
```
db_host = "localhost"
db_user = "user name"
db_pass = "password"
database= "Weather"
```


