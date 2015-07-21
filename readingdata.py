from struct import *
import pygame, sys
from pygame.locals import *
import math

WindowSizeX = 1700
WindowSizeY = 320
pygame.init()
DISPLAYSURF = pygame.display.set_mode((WindowSizeX,WindowSizeY))
pygame.display.set_caption('Graph')

Red = (255, 0, 0)
Green = (0, 255, 0)
Blue = (0, 0, 255)
Cyan = (0, 255, 255)
Magenta = (255, 0, 255)
Yellow = (255, 255, 0)


stepstart = []
stepamount = 10
steplenav = 0

Xsavelist = []
Ysavelist = []
Zsavelist = []

gXsavelist = []
gYsavelist = []
gZsavelist = []

startOfGraph = 0 # start time in milliseconds
lengthOfGraph = 50000 # length of graph in milliseconds
msPerPixel = lengthOfGraph/WindowSizeX
groundContactTime = 30 # expected ground time in milliseconds, used to calibrate gyroscope
groundAccellerationMargin = 0.30 #margin for calibrating

f = open('data_20150629142500_168.bin', 'rb')

class Vector(object):
	def __init__ (self, X, Y, Z):
		self.vecX = X
		self.vecY = Y
		self.vecZ = Z
	def printVector(self):
		print('(', self.vecX, ',',  self.vecY, ',', self.vecZ, ')', '\n')

class Matrix(object):
	def __init__(self, xx, xy, xz, yx, yy, yz, zx, zy, zz):
		self.mXX = xx #topleft
		self.mXY = xy
		self.mXZ = xz #topright
		self.mYX = yx
		self.mYY = yy
		self.mYZ = yz
		self.mZX = zx #bottomleft
		self.mZY = zy
		self.mZZ = zz #bottomright
	def remakeall(self, xx, xy, xz, yx, yy, yz, zx, zy, zz):
		self.mXX = xx #topleft
		self.mXY = xy
		self.mXZ = xz #topright
		self.mYX = yx
		self.mYY = yy
		self.mYZ = yz
		self.mZX = zx #bottomleft
		self.mZY = zy
		self.mZZ = zz #bottomright
		
	def MultiplyMatrix(self, RHS):
		mXXtemp = self.mXX * RHS.mXX + self.mXY * RHS.mYX + self.mXZ * RHS.mZX
		mXYtemp = self.mXX * RHS.mXY + self.mXY * RHS.mYY + self.mXZ * RHS.mZY
		mXZtemp = self.mXX * RHS.mXZ + self.mXY * RHS.mYZ + self.mXZ * RHS.mZZ

		mYXtemp = self.mYX * RHS.mXX + self.mYY * RHS.mYX + self.mYZ * RHS.mZX
		mYYtemp = self.mYX * RHS.mXY + self.mYY * RHS.mYY + self.mYZ * RHS.mZY
		mYZtemp = self.mYX * RHS.mXZ + self.mYY * RHS.mYZ + self.mYZ * RHS.mZZ

		mZXtemp = self.mZX * RHS.mXX + self.mZY * RHS.mYX + self.mZZ * RHS.mZX
		mZYtemp = self.mZX * RHS.mXY + self.mZY * RHS.mYY + self.mZZ * RHS.mZY
		mZZtemp = self.mZX * RHS.mXZ + self.mZY * RHS.mYZ + self.mZZ * RHS.mZZ
		
		self.mXX = mXXtemp
		self.mXY = mXYtemp
		self.mXZ = mXZtemp

		self.mYX = mYXtemp
		self.mYY = mYYtemp
		self.mYZ = mYZtemp

		self.mZX = mZXtemp
		self.mZY = mZYtemp
		self.mZZ = mZZtemp

	def MultiplyVector(self, theVector):
		vecXtemp = self.mXX * theVector.vecX + self.mXY * theVector.vecY + self.mXZ * theVector.vecZ
		vecYtemp = self.mYX * theVector.vecX + self.mYY * theVector.vecY + self.mYZ * theVector.vecZ
		vecZtemp = self.mZX * theVector.vecX + self.mZY * theVector.vecY + self.mZZ * theVector.vecZ
		
		theVector.vecX = vecXtemp
		theVector.vecY = vecYtemp
		theVector.vecZ = vecZtemp
	
	def printMatrix(self):
		print('(', self.mXX, ',',  self.mXY, ',', self.mXZ, ')')
		print('(', self.mYX, ',',  self.mYY, ',', self.mYZ, ')')
		print('(', self.mZX, ',',  self.mZY, ',', self.mZZ, ')', '\n')
		
for i in range (0,startOfGraph):
	(t, ax, ay, az, temp, gx, gy, gz, dummy) = unpack('qfffffffi', f.read (40))
for i in range (0,lengthOfGraph):
	try:
		(t, ax, ay, az, temp, gx, gy, gz, dummy) = unpack('qfffffffi', f.read (40))
	#	print (i, t, ax, ay, az, temp, gx, gy, gz, dummy, '\n')
		if ay > 7 and (len(stepstart) == 0 or i > stepstart[-1]+400):
			stepstart.append(i)
		Xsavelist.append(ax)
		Ysavelist.append(ay)
		Zsavelist.append(az)	
		gXsavelist.append(gx/16*2*math.pi/1000)
		gYsavelist.append(gy/16*2*math.pi/1000)
		gZsavelist.append(gz/16*2*math.pi/1000)
	except error:
		print("no more to unpack", i)
		msPerPixel = i/WindowSizeX
		break
		
	
MainMatrix = Matrix(1, 0, 0, 0, 1, 0, 0, 0, 1)
AddedXMatrix = Matrix(1, 0, 0, 0, 1, 0, 0, 0, 1)
AddedYMatrix = Matrix(1, 0, 0, 0, 1, 0, 0, 0, 1)
AddedZMatrix = Matrix(1, 0, 0, 0, 1, 0, 0, 0, 1)

groundedTime = 0
for i in range(0,(len(gXsavelist))):
	if Xsavelist[i] > -groundAccellerationMargin and Xsavelist[i] < groundAccellerationMargin and Zsavelist[i] > -groundAccellerationMargin and Zsavelist[i] < groundAccellerationMargin:
		groundedTime = groundedTime + 1
	else:
		groundedTime = 0
	if groundedTime >= groundContactTime:
		MainMatrix.remakeall(1, 0, 0, 0, 1, 0, 0, 0, 1)
	AddedXMatrix.remakeall(1, 0, 0, 0, math.cos(gXsavelist[i]), -(math.sin(gXsavelist[i])), 0, math.sin(gXsavelist[i]), math.cos(gXsavelist[i]))
	AddedYMatrix.remakeall(math.cos(gYsavelist[i]), 0, math.sin(gYsavelist[i]), 0, 1, 0, -(math.sin(gYsavelist[i])), 0, math.cos(gYsavelist[i]))
	AddedZMatrix.remakeall(math.cos(gZsavelist[i]), -(math.sin(gZsavelist[i])), 0, math.sin(gZsavelist[i]), math.cos(gZsavelist[i]), 0, 0, 0, 1)

	MainMatrix.MultiplyMatrix(AddedXMatrix)
	MainMatrix.MultiplyMatrix(AddedYMatrix)
	MainMatrix.MultiplyMatrix(AddedZMatrix)

	pygame.draw.rect(DISPLAYSURF, Cyan, (i/msPerPixel, math.ceil((-Xsavelist[i]+16)*10), 2, 2))
	pygame.draw.rect(DISPLAYSURF, Magenta, (i/msPerPixel, math.ceil((-Ysavelist[i]+16)*10), 2, 2))
	pygame.draw.rect(DISPLAYSURF, Yellow, (i/msPerPixel, math.ceil((-Zsavelist[i]+16)*10), 2, 2))

	pygame.draw.rect(DISPLAYSURF, Red, (i/msPerPixel, math.ceil((-MainMatrix.mXX)*160 + 160), 3, 3))
	pygame.draw.rect(DISPLAYSURF, Green, (i/msPerPixel, math.ceil((-MainMatrix.mYX)*160 + 160), 3, 3))
	pygame.draw.rect(DISPLAYSURF, Blue, (i/msPerPixel, math.ceil((-MainMatrix.mZX)*160 + 160), 3, 3))
#	print(i, MainMatrix.mXX, MainMatrix.mYX, MainMatrix.mZX)
	
#for i in range(0, stepamount):
#	steplenav = steplenav + (stepstart[i+1]-stepstart[i])
#steplenav = math.ceil(steplenav / stepamount)	

#stepamount = len(stepamount) - 5

#for i in range(0, steplenav):
#	Xaverage = 0
#	Yaverage = 0
#	Zaverage = 0
#	for j in range (0, stepamount):
#		Xaverage = Xaverage + Xsavelist[stepstart[j]+i]
#		Yaverage = Yaverage + Ysavelist[stepstart[j]+i]
#		Zaverage = Zaverage + Zsavelist[stepstart[j]+i]
#	Xaverage = (Xaverage/stepamount)
#	Yaverage = (Yaverage/stepamount)
#	Zaverage = (Zaverage/stepamount)
#	pygame.draw.rect(DISPLAYSURF, Red, (i, math.ceil((-Xaverage+16)*10) , 3, 3))	
#	pygame.draw.rect(DISPLAYSURF, Green, (i, math.ceil((-Yaverage+16)*10) , 3, 3))	
#	pygame.draw.rect(DISPLAYSURF, Blue, (i, math.ceil((-Zaverage+16)*10) , 3, 3))	

pygame.display.update()	

s = input('--> ')