import epuck_basic as epb
import prims1
import imagepro
import math
import random

class Swarm(epb.EpuckBasic):
	
	def __init__(self):
		epb.EpuckBasic.__init__(self)
		self.basic_setup() # defined for EpuckBasic
		self.recovering = False 
		self.last_data = None
		self.stagnation_threshold = 0.001
		self.stag_count = 0

	def run(self,steps = 500):
		i = 0
		while True:
			light = [(x/4096.0) for x in self.get_lights()]
			for i in range(len(light)):
				if math.isnan(light[i]):
					light[i] = 0.0
			self.get_led()
			motor_action = [0.0, 0.0]
			if self.use_stag(light):
				motor_action = self.stagnation(light)
			elif self.use_ret(light):
				motor_action = self.retrieval(light)
			else:
				motor_action = self.search(light)
			print motor_action
			self.set_wheel_speeds(motor_action[0], motor_action[1])
			self.run_timestep()
	
	def search(self, light):
		light_left = sum(light[1:4])
		light_right = sum(light[5:]) # all
		
		motor_action = [0.0, 0.0]
		if light_right - light_left < 0: # more light on the left side
			motor_action[0] = 1.0
			motor_action[1] = -1.0
		else: # more light on the right side
			motor_action[0] = -1.0
			motor_action[1] = 1.0
		if light[0] + light[7] < light[3] + light[4]:
			motor_action[0] = 1.0
			motor_action[1] = -1.0
		return motor_action
	
	def retrieval(self, light):
		return [1.0, 1.0]
	
	def stagnation(self, light):
		motor_action = [-1.0, -1.0]
		if self.stag_count > 50:
			motor_action[0] = self.stag_count*0.01
		if self.stag_count > 100:
			self.stag_count = 0
			self.recovering = False
		self.stag_count += 1
		return motor_action
		
	def use_ret(self, light):
		if light[0] > 0.99: # If the IR-light is right in front of the robot
			return True
		return False
		
	def use_stag(self, light):
		if self.recovering:
			return True
		if self.last_data:
			if (abs(self.last_data[0] - light[0]) < self.stagnation_threshold
			  or self.last_data == light):
				self.stag_count += 1
				if self.stag_count > 200:
					self.stag_count = 0
					self.recovering = True
					return True
		self.last_data = light
		return False

swarm = Swarm()
swarm.run()
