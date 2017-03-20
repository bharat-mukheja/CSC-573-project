import sys
from subprocess import Popen
import os

import json

import time
import calendar

import random

def mainloop(trafficType, max_volume):

	FNULL = open(os.devnull, "w")
	traffic_volume = 0
	targets = []
	num_targets = -1
	iperf_singles = []

	if trafficType == 1:
		#Constant
		cap_volume = max_volume
	elif trafficType == 2:
		#Increasing
		cap_volume = 0
	elif trafficType == 3:
		#Pulse
		cap_volume = 0
		sleep_duration = 100
	elif trafficType == 4:
		#Random
		cap_volume = max_volume	

	with open('targets.json') as target_file:    
		saved_targets = json.load(target_file)
		for target in saved_targets['targets']:
			targets.append(target)
			num_targets += 1

#	print_counter = 0
	while True:
		time.sleep(.05)

		for iperf in iperf_singles:
			if iperf.checkTime():
				traffic_volume -= iperf.volume
				iperf_singles.remove(iperf)

		if trafficType == 2:
			if cap_volume < max_volume:
				cap_volume += max_volume / 1000
		elif trafficType == 3:
			sleep_duration -= 1
			if sleep_duration == 0:
				cap_volume = max_volume
			if sleep_duration == -100:
				cap_volume = 0
				sleep_duration = 100 
		elif trafficType == 4:
			cap_volume = cap_volume

		if traffic_volume < cap_volume:
			open_volume = cap_volume - traffic_volume
			target = random.randint(0, num_targets)
			new_volume = int(open_volume * random.uniform(.1, .2))


#			print_counter += 1
#			if print_counter > 10:
#				print("Cap Volume" + str(cap_volume))
#				print("Traffic Volume" + str(traffic_volume))
#				print("Open Volume" + str(open_volume))
#				print("New Volume" + str(new_volume))
#				print_counter = 0			

			if new_volume < 20:
				new_volume = int(open_volume * random.uniform(.25, .75))
				if new_volume < 20:
					continue

			traffic_volume += new_volume
			print("Current Volume: " + str(traffic_volume))

			if random.randint(0, 1):
				Popen(["iperf", "-c", str(targets[target]), "-p 2001", "-b", str(new_volume) + "K", "-t", "5", "-i", "1"], stdout=FNULL, stderr=FNULL)
			else:
				Popen(["iperf", "-u", "-c", str(targets[target]), "-p 2002", "-b", str(new_volume) + "K", "-t", "5", "-i", "1", "-S", "0x28"], stdout=FNULL, stderr=FNULL)
			
			iperf_singles.append( iperfSingle(targets[target], new_volume, calendar.timegm(time.gmtime()) + 5))


				

		



def outputTypes():
	print("CrossTraffic Types:")
	print("cons: constant traffic")
	print("incr: increasing traffic")
	print("puls: pulsating traffic")
	print("rand: random traffic")
	sys.exit()

class iperfSingle:
	def __init__(self, target, volume, endtime):
		self.target = target
		self.volume = volume
		self.endtime = endtime

	def checkTime(self):
		if self.endtime <= calendar.timegm(time.gmtime()):
			return True
		else:
			return False
	
		

if __name__ == "__main__":
	if len(sys.argv) == 1:
		outputTypes()
	elif len(sys.argv) == 2:
		print("Usage: [traffic type] [bandwidth in kB]")
		sys.exit()

	volume = int(sys.argv[2])

	if sys.argv[1] == "cons":
		mainloop(1, volume)
	elif sys.argv[1] == "incr":
		mainloop(2, volume)
	elif sys.argv[1] == "puls":
		mainloop(3, volume)
	elif sys.argv[1] == "rand":
		mainloop(4, volume)
	else:
		outputTypes()
