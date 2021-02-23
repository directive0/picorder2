print("Loading Python IL Module")

# PILgraph is here because both the black and white and colour screens need it.

from objects import *
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

import numpy
from array import *

# The following class is used to prepare sensordata for display on the graph and draw it to the screen.
class graphlist(object):

	# the following is constructor code to give each object a list suitable for storing all our graph data.
	def __init__(self, ident, graphcoords, graphspan, cycle = 0, colour = 0, width = 1):
		self.new = True
		self.cycle = cycle
		self.tock = timer()
		self.tock.logtime()
		self.glist = array('f', [])
		self.dlist = array('f', [])
		self.colour = colour
		self.auto = True
		self.width = width
		self.dotw = 6
		self.doth = 6

		self.datahigh = 0
		self.datalow = 0
		self.newrange = (self.datalow,self.datahigh)

		# stores the graph identifier
		self.ident = ident

		# collect data for where the graph should be drawn to screen.
		self.x, self.y = graphcoords
		self.spanx,self.spany = graphspan

		self.newx,self.newy = graphcoords
		self.newspanx,self.newspany = graphspan

		self.targetrange = ((self.y + self.spany), self.y)

		# seeds a list with the coordinates for 0 to give us a list that we can put our scaled graph values in
		for i in range(self.spanx):
			self.glist.append(self.y + self.spany)

		# seeds a list with sourcerange zero so we can put our sensor readings into it.
		for i in range(self.spanx):
			self.dlist.append(self.low)


	# the following function returns the graph list.
	def grabglist(self):
		return self.glist
	# the following function returns the data list.
	def grabdlist(self):
		return self.dlist

	# Returns the average of the current dataset
	def get_average(self):
		average = sum(self.buff) / len(self.buff)
		return average

	def get_high(self):
		return max(self.buff)

	def get_low(self):
		return min(self.buff)

	# this function calculates the approximate time scale of the graph
	def giveperiod(self):
		self.period = (self.spanx * self.cycle) / 60

		return self.period

	# the following appends data to the list.

	def update(self, data):
		# grabs a tuple to hold our values
		self.buff = self.grabdlist()


		# if the time elapsed has reached the set interval then collect data
		if self.tock.timelapsed() >= self.cycle:

			# we load new data from the caller
			self.cleandata = data

			#append it to our list of clean data
			self.buff.append(self.cleandata)

			#pop the oldest value off
			# may remove this
			self.buff.pop(0)
			self.tock.logtime()



	# the following pairs the list of values with coordinates on the X axis. The supplied variables are the starting X coordinates and spacing between each point.
	# if the auto flad is set then the class will autoscale the graph so that the highest and lowest currently displayed values are presented.
	def graphprep(self,datalist):
		self.linepoint = self.x
		self.jump = 1
		self.newlist = array('f', [])


		# get the range of the data.
		self.datahigh = max(self.dlist)
		self.datalow = min(self.dlist)
		self.newrange = (self.datalow,self.datahigh)

		# grabs the currently selected sensors range data
		sourcelow = configure.sensors[self.ident][1]
		sourcehigh = configure.sensors[self.ident][2]
		self.sourcerange = [sourcelow,sourcehigh]

		# for each vertical bar in the graph size
		for i in range(self.spanx):
			# if auto scaling is on
			if self.auto == True:
				# take the sensor value received and map it against the on screen limits
				scaledata = numpy.interp(datalist[i],self.newrange,self.targetrange)
			else:
				# use the sensors stated limits as the range.
				scaledata = numpy.interp(datalist[i],self.sourcerange,self.targetrange)


			self.newlist.append((self.linepoint,scaledata))

			self.linepoint = self.linepoint + self.jump

		return self.newlist

	def render(self, draw, auto = True, dot = True):

		self.auto = configure.auto[0]

		#preps the list by adding the X coordinate to every sensor value
		cords = self.graphprep(self.buff)

		# draws the line graph
		draw.line(cords,self.colour,self.width)


		if dot:
			x1 = cords[-1][0] - (self.dotw/2)
			y1 = cords[-1][1] - (self.doth/2)
			x2 = cords[-1][0] + (self.dotw/2)
			y2 = cords[-1][1] + (self.doth/2)
			draw.ellipse([x1,y1,x2,y2],self.colour)
