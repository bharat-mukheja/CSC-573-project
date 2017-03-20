||------------------------------------------------------------------||
||------------------------------------------------------------------||
||			Readme - bkmukhej,cfernan3,kgondha,rtwilli7				||
||------------------------------------------------------------------||
||------------------------------------------------------------------||


A- Before running this code, make sure that all the dependencies are met. The following python packages must be installed on the system - 
requests,
json,
thread,
threading,
time. 

If any of the package is not installed, install it via pip. If pip is absent, install it via apt-get install pip.

We are using floodlight controller for our project, so make sure to have a floodlight controller copy on machine and prebuilt
1. Turn ON the controller by entering the controller folder and launching the file "java -jar target/floodlight.jar"
2. To understand how the Traffic Generator is working, please refer to file "Traffic_Generator_Readme.txt"
3. Keep all the files in the zip in a single folder separate from the controller folder.
4.  (a) For first part of experiment, run the Traffic Generator.py and stream video from Multimedia Server 2
	(b) For second part of experiment, run the Traffic Generator. py as well as Controller_General_2.py and stream video from the Multimedia Server 1