print("Loading Python IL Module")


# PILgraph provides an object (graphlist) that will draw a new graph each frame.
# It was written to contain memory of the previous sensor readings, but this
# feature is no longer necessary.

# To do:
# - request from PLARS the N most recent values for the sensor assigned to this identifier



# it is initialized with:
# - a graph identifier so it knows which sensor to grab data for
# -

from objects import *
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

import numpy
from array import *
from plars import *

class graph_area(object):


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

		# stores the graph identifier, there are three on the multiframe
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
			self.dlist.append(self.datalow)


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

	# returns the highest
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
		# grabs the datalist
		self.buff = self.dlist


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



	# the following pairs the list of values with coordinates on the X axis.
	# The supplied variables are the starting X coordinates and spacing between each point.
	# if the auto flag is set then the class will autoscale the graph so that
	# the highest and lowest currently displayed values are presented.
	# takes in a list/array with length => span
	def graphprep(self,datalist):

		print('list length: ', len(datalist), ' ', "spanx: ", self.spanx)
		self.linepoint = self.x
		self.jump = 1
		self.newlist = [] #array('f', [])


		# get the range of the data.
		self.datahigh = max(self.dlist)
		self.datalow = min(self.dlist)
		self.newrange = (self.datalow,self.datahigh)

		# grabs the currently selected sensors range data
		sourcelow = configure.sensor_info[configure.sensors[self.ident][0]][1]

		sourcehigh = configure.sensor_info[configure.sensors[self.ident][0]][2]
		self.sourcerange = [sourcelow,sourcehigh]

		# for each vertical bar in the graph size
		for i in range(self.spanx):
			# if auto scaling is on
			if i < len(datalist):
				if self.auto == True:
					# take the sensor value received and map it against the on screen limits

					scaledata = numpy.interp(datalist[i],self.newrange,self.targetrange)
				else:
					# use the sensors stated limits as the range.
					scaledata = numpy.interp(datalist[i],self.sourcerange,self.targetrange)

				# append the current x position, with this new scaled data as the y positioning into the buffer
				self.newlist.append((self.linepoint,scaledata))
			else:
				self.newlist.append((self.linepoint,sourcelow))


				# increment the cursor
				self.linepoint = self.linepoint + self.jump


		return self.newlist

	def render(self, draw, auto = True, dot = True):

		self.auto = configure.auto[0]

		dsc = configure.sensor_info[configure.sensors[self.ident][0]][3]
		dev = configure.sensor_info[configure.sensors[self.ident][0]][5]
		print("dev,dsc: ", dsc,",",dev)
		#preps the list by adding the X coordinate to every sensor value
		cords = self.graphprep(plars.get_recent(dsc,dev,num = self.spanx))

		# draws the line graph
		draw.line(cords,self.colour,self.width)


		if dot:
			x1 = cords[-1][0] - (self.dotw/2)
			y1 = cords[-1][1] - (self.doth/2)
			x2 = cords[-1][0] + (self.dotw/2)
			y2 = cords[-1][1] + (self.doth/2)
			draw.ellipse([x1,y1,x2,y2],self.colour)
