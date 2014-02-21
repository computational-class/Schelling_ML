'''
Quick implementation of the Schelling segregation mode, in order to generate
data for an ABM machine learning experiment.
'''

import random
import numpy as np
import csv

class Model(object):
	'''
	Hard-coded Schelling model with agent types 1, 2, a 10x10 grid, 
	80% full and 20% of agents of type 2.
	'''

	def __init__(self):
		# World size:
		self.width = 10
		self.height = 10

		# Agent characteristics
		self.density = 0.8 # Probability of an agent in any cell
		self.minority = 0.2  # Probability of a type 2 agent.

		# Agent behavior:
		self.desired_similar = 3

		self.all_agents = []
		self.grid = np.empty((self.width, self.height), dtype=object)

		# Populate the grid:
		i = 0
		for x in range(self.width):
			for y in range(self.height):
				if random.random() > self.density: continue
				agent_type = 1
				if random.random() < self.minority:
					agent_type = 2
				new_agent = Agent(self, agent_type, i, (x,y))
				self.grid[x,y] = new_agent
				self.all_agents.append(new_agent)
				i += 1

		# Start the step counter:
		self.steps = 0

		# The data collection object:
		self.log = []
		header = ["Step", "Agent_ID", "Agent_Type"]
		for i in range(8):
			header.append("Neighbor_"+str(i))
		header.append("Happy?")
		self.log.append(header)

	def step(self):
		flag = True
		for a in self.all_agents:
			if a.step(): # If this agent has moved, set flag to false.
				flag = False
		self.steps += 1
		return flag


	def move(self, start, end):
		'''
		Move the agent at start to end

		Args:
			start, end: tuples of (x,y) values
		'''
		if self.grid[end] is not None:
			raise KeyError("Target space is not empty!")

		a = self.grid[start]
		self.grid[start] = None
		self.grid[end] = a
		a.location = end

	def get_empty_cells(self):
		'''
		Find a list of empty cell coordinates.
		'''
		empty_cells = []
		for x in range(self.width):
			for y in range(self.height):
				if self.grid[x,y] is None:
					empty_cells.append((x,y))
		return empty_cells

	def get_cell(self, x, y):
		'''
		Get the contents of cell (x,y), assuming the grid is toroidal.
		'''
		new_x = self.get_x(x)
		new_y = self.get_y(y)
		return self.grid[new_x, new_y]

	def get_x(self, x):
		if x >= 0 and x < self.width:
			return x
		elif x < 0:
			return self.width + x
		elif x >= self.width:
			return x - self.width

	def get_y(self, y):
		if y >= 0 and y < self.height:
			return y
		elif y < 0:
			return self.height + y
		elif y >= self.height:
			return y - self.height

	def export_log(self, file_path):
		f = open(file_path, "wb")
		writer = csv.writer(f)
		for entry in self.log:
			writer.writerow(entry)
		f.close()



class Agent(object):
	def __init__(self, model, agent_type, id_num, location):
		'''
		New Schelling agent
		'''
		self.model = model
		self.type = agent_type
		self.id_num = id_num
		self.location = location


	def step(self):
		'''
		A single model step. Returns True if the agent has moved.
		'''
		neighbors = []
		x, y = self.location
		for dx in [-1, 0, 1]:
			for dy in [-1, 0, 1]:
				if dy == dx == 0: continue
				a = self.model.get_cell(x+dx, y+dy)
				if a is None: 
					neighbors.append(0)
				else:
					neighbors.append(a.type)
		similar = [n for n in neighbors if n == self.type]
		if len(similar) >= self.model.desired_similar:
			happy = 1
		else:
			happy = 0

		# Log this step:
		log_entry = [self.model.steps, self.id_num, self.type]
		log_entry += neighbors
		log_entry.append(happy)
		self.model.log.append(log_entry)


		# If unhappy, move
		if not happy:
			possible_moves = self.model.get_empty_cells()
			dest = random.choice(possible_moves)
			self.model.move(self.location, dest)
			return True # Moved
		else:
			return False # Didn't move

	def decision(self, neighbors):
		'''
		Decide whether or not to move, based on the neighbors' types.
		'''
		similar = [n for n in neighbors if n == self.type]
		if len(similar) >= self.model.desired_similar:
			return False
		else:
			return True



