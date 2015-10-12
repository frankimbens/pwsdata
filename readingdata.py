from struct import *
import pygame, sys
from pygame.locals import *
import math

WindowSizeX = 1700
WindowSizeY = 640
pygame.init()
DISPLAYSURF = pygame.display.set_mode((WindowSizeX,WindowSizeY))
pygame.display.set_caption('Graph')

Red = (255, 0, 0)
Green = (0, 255, 0)
Blue = (0, 0, 255)
Cyan = (0, 255, 255)
Magenta = (255, 0, 255)
Yellow = (255, 255, 0)
Black = (0, 0, 0)
White = (255, 255, 255)

FrontLanding = []
BackLanding = []
FrontLandingI = []
BackLandingI = []
stepamount = 10
steplenav = 0

XsavelistFront = []
YsavelistFront = []
ZsavelistFront = []

aXsavelistFront = []
aYsavelistFront = []
aZsavelistFront = []

gXsavelistFront = []
gYsavelistFront = []
gZsavelistFront = []

XsavelistBack = []
YsavelistBack = []
ZsavelistBack = []

aXsavelistBack = []
aYsavelistBack = []
aZsavelistBack = []

gXsavelistBack = []
gYsavelistBack = []
gZsavelistBack = []

timesavelistFront = []
timesavelistBack = []

startOfGraph = 0 # start time in milliseconds
lengthOfGraph = 5000000 # length of graph in milliseconds
msPerPixel = lengthOfGraph/WindowSizeX
zoomLevel = 1
startDrawPos = 0
groundContactTime = 16 # expected ground time in milliseconds, used to calibrate gyroscope
groundAccellerationMargin = 0.30 #margin for calibrating

SensorFront = open('data_20150830141908_169.bin', 'rb')
SensorBack =  open('data_20150830141908_168.bin', 'rb')

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
	(t, ax, ay, az, temp, gx, gy, gz, dummy) = unpack('qfffffffi', SensorFront.read (40))
	(t, ax, ay, az, temp, gx, gy, gz, dummy) = unpack('qfffffffi', SensorBack.read (40))
	print("Start cut off")
	
lookForFront = True
lookForBack = True

t = 0
tb = 0
	
for i in range (0,lengthOfGraph): # reading data
	try:
		if t <= tb: #front sensor
			(t, ax, ay, az, temp, gx, gy, gz, dummy) = unpack('qfffffffi', SensorFront.read (40))
			XsavelistFront.append(ax)
			YsavelistFront.append(ay)
			ZsavelistFront.append(az)	
			gXsavelistFront.append(gx/16*2*math.pi/1000)
			gYsavelistFront.append(gy/16*2*math.pi/1000)
			gZsavelistFront.append(gz/16*2*math.pi/1000)
			timesavelistFront.append(math.ceil(t/1000))
			if ay > 7 and (len(FrontLanding) == 0 or t > FrontLanding[-1]+400): #check landing
				FrontLanding.append(math.ceil(t))
				FrontLandingI.append(i)
				lookForBack = True
				lookForFront = False
		if tb < t: #back sensor
			(tb, axb, ayb, azb, tempb, gxb, gyb, gzb, dummy) = unpack('qfffffffi', SensorBack.read (40))
			XsavelistBack.append(axb)
			YsavelistBack.append(ayb)
			ZsavelistBack.append(azb)	
			gXsavelistBack.append(gxb/16*2*math.pi/1000)
			gYsavelistBack.append(gyb/16*2*math.pi/1000)
			gZsavelistBack.append(gzb/16*2*math.pi/1000)
			timesavelistBack.append(math.ceil(tb/1000))
#			if lookForBack == True and ayb > 7 and (len(BackLanding) == 0 or t/1000 > BackLanding[-1]+400):
#				BackLanding.append(math.ceil(tb/1000))
#				BackLandingI.append(i)
#				lookForBack = False
#				lookForFront = True
	#	print (i, t, ax, ay, az, temp, gx, gy, gz, dummy, '\n')
		

	except error:
		print("no more to unpack", i)
		msPerPixel = i/WindowSizeX
		lengthOfGraph = i
		break

	
for i in range (0, len(FrontLandingI)):
	BackLandingI.append(FrontLandingI[i])
	BackLanding.append(FrontLanding[i])

"""	
for i in range (0, len(FrontLandingI)):
	for j in range (0,200):
		ka = FrontLandingI[i] - j
		kb = FrontLandingI[i] + j
		if ka > 0 and ka < len(YsavelistBack):
			if YsavelistBack[ka] > 7:
				BackLandingI[i] = (ka)
				BackLanding[i] = (math.ceil(timesavelistBack[ka]))
				break
		if kb > 0 and kb < len(YsavelistBack):
			if YsavelistBack[kb] > 7:
				BackLandingI[i] = (kb)
				BackLanding[i] = (math.ceil(timesavelistBack[kb]))
				break
"""

j = 0
for i in range (0, len(YsavelistBack)):
	if math.ceil(timesavelistBack[i]) > FrontLanding[j]+200 and j + 1 < len(FrontLanding):
		j = j + 1
	elif math.ceil(timesavelistBack[i]) >= FrontLanding[j] - 200 and math.ceil(timesavelistBack[i]) <= FrontLanding[j] + 200 and YsavelistBack[i] > 10:
		BackLanding[j] = math.ceil(timesavelistBack[i])
		BackLandingI[j] = i
		

		
		
MainMatrixFront = Matrix(1, 0, 0, 0, 1, 0, 0, 0, 1)
MainMatrixBack = Matrix(1, 0, 0, 0, 1, 0, 0, 0, 1)
AddedXMatrix = Matrix(1, 0, 0, 0, 1, 0, 0, 0, 1)
AddedYMatrix = Matrix(1, 0, 0, 0, 1, 0, 0, 0, 1)
AddedZMatrix = Matrix(1, 0, 0, 0, 1, 0, 0, 0, 1)
AccelerationVector = Vector(0, 0, 0)

#MatrixListFront = [Matrix(1, 0, 0, 0, 1, 0, 0, 0, 1) for i in range(lengthOfGraph)]
#MatrixListBack = [Matrix(1, 0, 0, 0, 1, 0, 0, 0, 1) for i in range(lengthOfGraph)]

groundedTime = 0
for i in range(0,(len(gXsavelistFront))): # matrix calculations
	if XsavelistFront[i] > -groundAccellerationMargin and XsavelistFront[i] < groundAccellerationMargin and ZsavelistFront[i] > -groundAccellerationMargin and ZsavelistFront[i] < groundAccellerationMargin:
		groundedTime = groundedTime + 1
	else:
		groundedTime = 0
	if groundedTime >= groundContactTime:
		MainMatrixFront.remakeall(1, 0, 0, 0, 1, 0, 0, 0, 1)
		MainMatrixBack.remakeall(1, 0, 0, 0, 1, 0, 0, 0, 1)

	"""
	AddedXMatrix.remakeall(1, 0, 0, 0, math.cos(gXsavelistFront[i]), (math.sin(gXsavelistFront[i])), 0, -(math.sin(gXsavelistFront[i])), math.cos(gXsavelistFront[i]))
	AddedYMatrix.remakeall(math.cos(gYsavelistFront[i]), 0, -(math.sin(gYsavelistFront[i])), 0, 1, 0, (math.sin(gYsavelistFront[i])), 0, math.cos(gYsavelistFront[i]))
	AddedZMatrix.remakeall(math.cos(gZsavelistFront[i]), (math.sin(gZsavelistFront[i])), 0, -(math.sin(gZsavelistFront[i])), math.cos(gZsavelistFront[i]), 0, 0, 0, 1)

	MainMatrixFront.MultiplyMatrix(AddedXMatrix)
	MainMatrixFront.MultiplyMatrix(AddedYMatrix)
	MainMatrixFront.MultiplyMatrix(AddedZMatrix)
	
	AddedXMatrix.remakeall(1, 0, 0, 0, math.cos(gXsavelistBack[i]), (math.sin(gXsavelistBack[i])), 0, -(math.sin(gXsavelistBack[i])), math.cos(gXsavelistBack[i]))
	AddedYMatrix.remakeall(math.cos(gYsavelistBack[i]), 0, -(math.sin(gYsavelistBack[i])), 0, 1, 0, (math.sin(gYsavelistBack[i])), 0, math.cos(gYsavelistBack[i]))
	AddedZMatrix.remakeall(math.cos(gZsavelistBack[i]), (math.sin(gZsavelistBack[i])), 0, -(math.sin(gZsavelistBack[i])), math.cos(gZsavelistBack[i]), 0, 0, 0, 1)

	MainMatrixBack.MultiplyMatrix(AddedXMatrix)
	MainMatrixBack.MultiplyMatrix(AddedYMatrix)
	MainMatrixBack.MultiplyMatrix(AddedZMatrix)
	"""	

	"""	
	AccelerationVector.vecX = XsavelistFront[i]
	AccelerationVector.vecY = YsavelistFront[i]
	AccelerationVector.vecZ = ZsavelistFront[i]

	MainMatrixFront.MultiplyVector(AccelerationVector)

	aXsavelistFront.append(AccelerationVector.vecX)
	aYsavelistFront.append(AccelerationVector.vecY)
	aZsavelistFront.append(AccelerationVector.vecZ)
	"""

	"""
	MatrixListFront[i].mXX = MainMatrixFront.mXX
	MatrixListFront[i].mXY = MainMatrixFront.mXY
	MatrixListFront[i].mXZ = MainMatrixFront.mXZ

	MatrixListFront[i].mYX = MainMatrixFront.mYX
	MatrixListFront[i].mYY = MainMatrixFront.mYY
	MatrixListFront[i].mYZ = MainMatrixFront.mYZ

	MatrixListFront[i].mZX = MainMatrixFront.mZX
	MatrixListFront[i].mZY = MainMatrixFront.mZY
	MatrixListFront[i].mZZ = MainMatrixFront.mZZ

	MatrixListBack[i].mXX = MainMatrixBack.mXX
	MatrixListBack[i].mXY = MainMatrixBack.mXY
	MatrixListBack[i].mXZ = MainMatrixBack.mXZ

	MatrixListBack[i].mYX = MainMatrixBack.mYX
	MatrixListBack[i].mYY = MainMatrixBack.mYY
	MatrixListBack[i].mYZ = MainMatrixBack.mYZ

	MatrixListBack[i].mZX = MainMatrixBack.mZX
	MatrixListBack[i].mZY = MainMatrixBack.mZY
	MatrixListBack[i].mZZ = MainMatrixBack.mZZ
	"""
	
#	print(i, MainMatrixFront.mXX, MainMatrixFront.mYX, MainMatrixFront.mZX)
	
#for i in range(0, stepamount):
#	steplenav = steplenav + (stepstart[i+1]-stepstart[i])
#steplenav = math.ceil(steplenav / stepamount)	

#stepamount = len(stepamount) - 5

#for i in range(0, steplenav):
#	Xaverage = 0
#	Yaverage = 0
#	Zaverage = 0
#	for j in range (0, stepamount):
#		Xaverage = Xaverage + XsavelistFront[stepstart[j]+i]
#		Yaverage = Yaverage + YsavelistFront[stepstart[j]+i]
#		Zaverage = Zaverage + ZsavelistFront[stepstart[j]+i]
#	Xaverage = (Xaverage/stepamount)
#	Yaverage = (Yaverage/stepamount)
#	Zaverage = (Zaverage/stepamount)
#	pygame.draw.rect(DISPLAYSURF, Red, (i, math.ceil((-Xaverage+16)*10) , 3, 3))	
#	pygame.draw.rect(DISPLAYSURF, Green, (i, math.ceil((-Yaverage+16)*10) , 3, 3))	
#	pygame.draw.rect(DISPLAYSURF, Blue, (i, math.ceil((-Zaverage+16)*10) , 3, 3))	

Grabbed = False
isFirstLoop = True

while True:
	for event in pygame.event.get():
		if event.type == QUIT:
			pygame.quit()
			sys.exit()

	keys=pygame.key.get_pressed()
	Mouse1, Mouse2, Mouse3 = pygame.mouse.get_pressed()
	MouseX, MouseY = pygame.mouse.get_pos()
	
	if Grabbed == False:
		MouseXOld = MouseX
	
	if keys[K_LEFT]:
		zoomLevel = zoomLevel/1.03
	if keys[K_RIGHT]:
		zoomLevel = zoomLevel*1.03
	if Mouse1 == 1:
		Grabbed = True
		startDrawPos = startDrawPos - MouseXOld + MouseX
		MouseXOld = MouseX
	else:
		Grabbed = False
	
	pygame.draw.rect(DISPLAYSURF, Black, (0, 0, WindowSizeX, WindowSizeY))
	pixelPerPixel = WindowSizeX / len(FrontLanding)
	pixelPerMS = 1.0 / msPerPixel
	reDraw = 0
	pygame.draw.line(DISPLAYSURF, White, (1, WindowSizeY/2), (WindowSizeX, WindowSizeY/2), 2)

	for i in range(0,(len(XsavelistBack))):
		reDraw = reDraw + pixelPerMS*zoomLevel
#		print (timesavelistBack[i], pixelPerMS, 1.0/45)
		if math.ceil(timesavelistBack[i]*pixelPerMS*zoomLevel) + startDrawPos > 0 and math.ceil(timesavelistBack[i]*pixelPerMS*zoomLevel) + startDrawPos < WindowSizeX and reDraw >= 0.5:
			pygame.draw.rect(DISPLAYSURF, Cyan, (math.ceil(timesavelistFront[i]*pixelPerMS*zoomLevel) + startDrawPos, math.ceil((-XsavelistFront[i]+16)*20), 2, 2))
			pygame.draw.rect(DISPLAYSURF, Magenta, (math.ceil(timesavelistFront[i]*pixelPerMS*zoomLevel) + startDrawPos, math.ceil((-YsavelistFront[i]+16)*20), 2, 2))
			pygame.draw.rect(DISPLAYSURF, Yellow, (math.ceil(timesavelistFront[i]*pixelPerMS*zoomLevel) + startDrawPos, math.ceil((-ZsavelistFront[i]+16)*20), 2, 2))

			pygame.draw.rect(DISPLAYSURF, Red, (math.ceil(timesavelistBack[i]*pixelPerMS*zoomLevel) + startDrawPos, math.ceil((-XsavelistBack[i]+16)*20), 2, 2))
			pygame.draw.rect(DISPLAYSURF, Green, (math.ceil(timesavelistBack[i]*pixelPerMS*zoomLevel) + startDrawPos, math.ceil((-YsavelistBack[i]+16)*20), 2, 2))
			pygame.draw.rect(DISPLAYSURF, Blue, (math.ceil(timesavelistBack[i]*pixelPerMS*zoomLevel) + startDrawPos, math.ceil((-ZsavelistBack[i]+16)*20), 2, 2))
	
#			pygame.draw.rect(DISPLAYSURF, Red, (math.ceil(timesavelistFront[i]/msPerPixel*zoomLevel) + startDrawPos, math.ceil((-MatrixListFront[i].mXX)*320 + 320), 3, 3))
#			pygame.draw.rect(DISPLAYSURF, Green, (math.ceil(timesavelistFront[i]/msPerPixel*zoomLevel) + startDrawPos, math.ceil((MatrixListFront[i].mYX)*320 + 320), 3, 3))
#			pygame.draw.rect(DISPLAYSURF, Blue, (math.ceil(timesavelistFront[i]/msPerPixel*zoomLevel) + startDrawPos, math.ceil((MatrixListFront[i].mZX)*320 + 320), 3, 3))
			reDraw = 0
#			if isFirstLoop:
#				print (BackLanding[i], FrontLanding[i], BackLanding[i] - FrontLanding[i], math.ceil(320 - (BackLanding[i] - FrontLanding[i])/3.0))

	"""
	for i in range(0,(len(FrontLanding))):
		reDraw = reDraw + pixelPerPixel*zoomLevel
		if math.ceil(i*pixelPerPixel*zoomLevel) + startDrawPos > 0 and math.ceil(i*pixelPerPixel*zoomLevel) + startDrawPos < WindowSizeX and reDraw >= 1:
			if i > 0:
				pygame.draw.rect(DISPLAYSURF, Red, (math.ceil(i*pixelPerPixel*zoomLevel) + startDrawPos, math.ceil(320 - ((FrontLanding[i] - FrontLanding[i-1])/3.0)), 2, 2))
			if i < len(BackLanding):
				if FrontLanding[i] - BackLanding[i] > 0:
					pygame.draw.rect(DISPLAYSURF, Green, (math.ceil(i*pixelPerPixel*zoomLevel) + startDrawPos, math.ceil(320 - (FrontLanding[i] - BackLanding[i])/3.0), 2, 2))
				elif FrontLanding[i] - BackLanding[i] < 0:
					pygame.draw.rect(DISPLAYSURF, Blue, (math.ceil(i*pixelPerPixel*zoomLevel) + startDrawPos, math.ceil(320 - (FrontLanding[i] - BackLanding[i])/3.0), 2, 2))
				else:
					pygame.draw.rect(DISPLAYSURF, Yellow, (math.ceil(i*pixelPerPixel*zoomLevel) + startDrawPos, math.ceil(320 - (FrontLanding[i] - BackLanding[i])/3.0), 2, 2))
	"""			

	isFirstLoop = False
	pygame.display.update()	
