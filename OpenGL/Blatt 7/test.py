'''
S:	Hintergrund schwarz
W:	Hintergrund weiss
R:	Hintergrund rot
B	Hintergrund blau
G	Hintergrund gelb
s	Vordergrund schwarz
w	Vordergrund weiss
r	Vordergrund rot
b	Vordergrund blau
g	Vordergrund gelb
o	orthographische Projektion
p	perspektivische Projektion
x	im Uhrzeigersinn um x-Achse rotieren
X	gegen Uhrzeigersinn um x-Achse rotieren
y	im Uhrzeigersinn um y-Achse rotieren
Y	gegen Uhrzeigersinn um y-Achse rotieren
z	im Uhrzeigersinn um z-Achse rotieren
Z	gegen Uhrzeigersinn um z-Achse rotieren
m	Polygonnetz/ausgefuellte Oberflaechen
l	Licht ein/aus
h:	Schatten ein/aus
ESC:	beenden 
linke Muastaste:	rotieren
mittlere Maustaste:	zoom
rechte Maustaste:	verschieben
Die Normalen Stimmen noch nicht ganz, vielleicht haben Sie da bei der Abnahme einen Tipp fuer mich ^^
'''

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.arrays import vbo
from OpenGL.GL.shaders import *
from numpy import *
import math
from math import sqrt


# globals
my_vbo = None
doZoom = False
doRotation = False
doTranslation = False
solidMode = True
wireMode = False
orthoMode = True
perspectiveMode = False
light = True
shade = False
mouseLastX = None
mouseLastY = None
#angle = 10
newXPos = 0.0
newYPos = 0.0
zoomFactor = 0
rotateX, rotateY, rotateZ = 0, 0, 0
WIDTH, HEIGHT = 500, 500
aspect = float(WIDTH/HEIGHT)
fov = 45.0
near = 0.1
far = 100.0
rotateX, rotateY, rotateZ = 0, 0, 0
# color
black = (0.0,0.0,0.0,0.0)
white = (1.0,1.0,1.0,1.0)
blue = (0.0,0.0,1.0,0.0)
green = (0.0,1.0,0.0,0.0)
yellow = (1.0,1.0,0.0,0.0)
red = (1.0,0.0,0.0,0.0)
modelColor = blue[0],blue[1],blue[2]
# light
#lightPosition = [0.0, 1200.0, 1000.0, 0.0]
lightPosition = [0.0, 12.0, 10.0, 0.0]
boundingBox = []

angle = 0
actOri = matrix([[1,0,0,0], [0,1,0,0], [0,0,1,0], [0,0,0,1]])
startP = ()
axis = [1., 0., 0.]

# initialize openGL
def initGL(width, height):
	# Set  colors
	glClearColor(white[0],white[1],white[2],white[3])
	glColor(modelColor)
	# switch to projection matrix
	glMatrixMode(GL_PROJECTION)
	# set to 1
	glLoadIdentity()
	# Camera, multiply with new p-matrix
	glOrtho(-1.5, 1.5, -1.5, 1.5, -10.0, 10.0)
	# switch to modelview matrix
	glMatrixMode(GL_MODELVIEW)

# load obj File, init Bounding Box, init Faces
def initGeometryFromObjFile():
	global my_vbo, scaleFactor, center, data, boundingBox
	if len(sys.argv) == 1:
		print "python oglViewer_jberl001.py bunny.obj"
		sys.exit(-1)
	print "Used File: ", sys.argv[1]
	# load object
	objectVertices, objectNormals, objectFaces = loadOBJ(sys.argv[1]) 
	data = []
	# create boundingbox
	boundingBox = [map(min, zip(*objectVertices)), map(max, zip(*objectVertices))]
	#boundingBoxShadow = [[boundingBox[0][0], boundingBox[0][1]+boundingBox[1][1], boundingBox[0][2]], [boundingBox[1][0], boundingBox[1][1]+boundingBox[1][1], boundingBox[1][2]]]
	# center of boundingbox
	##center = [(x[0]+x[1])/2.0 for x in zip(*boundingBox)]
	center = [(x[0]+x[1])/2.0 for x in zip(*boundingBox)]
	#center = [center[0], center[1] + boundingBox[1][1], center[2]]
	# scale factor
	#scaleFactor = 2.0/max([(x[1]-x[0]) for x in zip(*boundingBoxShadow)])
	##scaleFactor = 2.0/max([(x[1]-x[0]) for x in zip(*boundingBox)])
	scaleFactor = 2.0/max([(x[1]-x[0]) for x in zip(*boundingBox)])
	vertCount = 0;
	i = 0

	for vertex in objectFaces:
		vn = int(vertex[0])-1
		nn = int(vertex[2])-1
		i += 1
		if objectNormals:
			data.append(objectVertices[vn] + objectNormals[nn])
			#data.append([objectVertices[vn][0], objectVertices[vn][1] + boundingBox[1][1], objectVertices[vn][2]] + objectNormals[nn])
			#print data[-1]
		else:
			i1 = int(vertex[0])-1
			i2 = int(vertex[1])-1
			i3 = int(vertex[2])-1
			normal = calNormals(objectVertices[i1], objectVertices[i2], objectVertices[i3])
			data.append(objectVertices[i1]+normal)
			data.append(objectVertices[i2]+normal)
			data.append(objectVertices[i3]+normal)
	my_vbo = vbo.VBO(array(data,'f'))
    
# loads obj-file and return three lists with object-vertices, object-normals and object-faces
def loadOBJ(filename):
	objectVertices = [] 
	objectNormals = []
	objectFaces =[] 
	data = []
	checkNormal = False
	checkFace = 0
	faceTemp = []
	for lines in file(filename):
		if lines.split():
			check = lines.split()[0]
			if check == 'v':
				objectVertices.append(map(float,lines.split()[1:]))
			if check == 'vn':
				checkNormal = True
				objectNormals.append(map(float,lines.split()[1:]))
			if check == 'f':
				first = lines.split()[1:]
				##if '//' not in first:
				if not checkNormal:
					objectFaces.append(map(float,lines.split()[1:]))
					
				else:
					for face in first:
						objectFaces.append(map(float,face.split('//')))
	for face in objectFaces:
		# missing vt
		if len(face) == 2:
			face.insert(1, 0.0)
		# missing vt and vn
		if len(face) == 1:
			face.insert(1, 0.0)
			face.insert(2, 0.0)
	#if not objectNormals:
	if False:
		i = 0
		for faces in objectFaces:
			i += 1
			if i%3==0:
				index = int(faces[0])
				#objectNormals.append()
				objectNormals.append(calNormals(objectVertices[index-3], objectVertices[index-2], objectVertices[index-1]))
				objectNormals.append(calNormals(objectVertices[index-3], objectVertices[index-2], objectVertices[index-1]))
				objectNormals.append(calNormals(objectVertices[index-3], objectVertices[index-2], objectVertices[index-1]))
				
	# missing normals
	#if not checkNormal and not checkFace:
	#	vertCount = 0
	#	for face in objectFaces:
	#		vertCount = vertCount + 1
	#		if vertCount%3 == 0:
	#			objectNormals.append(calNormals(objectFaces[vertCount-3], objectFaces[vertCount-2], objectFaces[vertCount-1]))
	#			vertCount = 0;##
			##vertCount = vertCount + 1
	return objectVertices, objectNormals, objectFaces
	
# calculate normals for triangles
def calNormals(p1, p2, p3):
	# p1, p2, p3, vector U = p2 - p1, vector V = p3 - p1, normal N = U x V :
	# Nx = UyVz - UzVy
	# Ny = UzVx - UxVz
	# Nz = UxVy - UyVx
	U = [p2[0]-p1[0], p2[1]-p1[1], p2[2]-p1[2]]
	V = [p3[0]-p1[0], p3[1]-p1[1], p3[2]-p1[2]]
	Nx = (U[1]*V[2]) - (U[2]*V[1])
	Ny = (U[2]*V[0]) - (U[0]*V[2])
	Nz = (U[0]*V[1]) - (U[1]*V[0])
	##vn = normalize_v3([Nx, Ny, Nz])
	vn = [Nx, Ny, Nz]
	#print vn
	return vn

def normalize_v3(arr):
	#print arr
	x = arr[0]/math.sqrt(arr[0]**2 + arr[1]**2 + arr[2]**2)
	y = arr[1]/math.sqrt(arr[0]**2 + arr[1]**2 + arr[2]**2)
	z = arr[2]/math.sqrt(arr[0]**2 + arr[1]**2 + arr[2]**2)
	norm = [x, y, z]                
	return norm

# mouse events
def mouse(button, state, x, y):
	global doRotation, doZoom, doRotation, doTranslation, mouseLastX, mouseLastY, startP, angle, axis, actOri
	mouseLastX, mouseLastY = None, None
	r = min(WIDTH, HEIGHT)/2.0
	# rotate object
	if button == GLUT_LEFT_BUTTON:
		if state == GLUT_DOWN:
			doRotation = True
			startP = projectOnSphere(x,y,r)
		if state == GLUT_UP:
			doRotation = False
			actOri = actOri*rotate(angle, axis)
			angle = 0
	# zoom
	if button == GLUT_MIDDLE_BUTTON:
		if state == GLUT_DOWN:
			doZoom = True
		if state == GLUT_UP:
			doZoom = False
	# translate
	if button == GLUT_RIGHT_BUTTON:
		if state == GLUT_DOWN:
			doTranslation = True
		if state == GLUT_UP:
			doTranslation = False

# mouse motion
def mouseMotion(x,y):
	global angle, doZoom, doRotation, doTranslation, scaleFactor, center, mouseLastX, mouseLastY, rotateX, rotateY, sceneWidth, sceneHeight, newXPos, newYPos, zoomFactor, actOri, axis
	xDiff = 0
	yDiff = 0
	# calc difference between coordinates
	if mouseLastX != None:
		xDiff = x - mouseLastX
	if mouseLastY != None:
		yDiff = y - mouseLastY
	# rotate
	if doRotation:
		r = min(WIDTH, HEIGHT)/2.0
		moveP = projectOnSphere(x,y,r)
		angle = arccos(dot(startP, moveP))
		axis = cross(startP, moveP)
	global sceneWidth, sceneHeight
	# zoom
	if doZoom:
		zScale = float(sceneHeight) / angle
		if yDiff != 0:
			zoomFactor += (yDiff / zScale)
			resizeViewport(sceneWidth, sceneHeight)
	# translatation
	if doTranslation:
		scale = float(sceneWidth) / 2.0
		if xDiff != 0:
			newXPos += xDiff / scale
		if yDiff != 0:
			newYPos += -yDiff / scale
	# remember last coordinates
	mouseLastX = x
	mouseLastY = y
	glutPostRedisplay()

# Keypress
def keyPressed(key, x, y):
	global frontColorIndex, backColorIndex, rotateX, rotateY, rotateZ, perspectiveMode, orthoMode, wireMode, solidMode, gridMode, light, shade, modelColor, boundingBox
	# close
	if key == '\x1b':
		sys.exit()
	if key == 's':
		modelColor = black[0],black[1],black[2]
		glColor(modelColor)
	if key == 'w':
		modelColor = white[0],white[1],white[2]
		glColor(modelColor)
	if key == 'r':
		modelColor = red[0],red[1],red[2]
		glColor(modelColor)
	if key == 'b':
		modelColor = blue[0],blue[1],blue[2]
		glColor(modelColor)
	if key == 'g':
		modelColor = yellow[0],yellow[1],yellow[2]
		glColor(modelColor)
	if key == 'S':
		glClearColor(black[0],black[1],black[2],black[3])
	if key == 'W':
		glClearColor(white[0],white[1],white[2],white[3])
	if key == 'R':
		glClearColor(red[0],red[1],red[2],red[3])
	if key == 'B':
		glClearColor(blue[0],blue[1],blue[2],blue[3])
	if key == 'G':
		glClearColor(yellow[0],yellow[1],yellow[2],yellow[3])
	# Rotate
	if key == 'x': 
		rotateX = rotateX + angle
	if key == 'X':
		rotateX = rotateX - angle
	if key == 'y': 
		rotateY = rotateY + angle
	if key == 'Y':
		rotateY = rotateY - angle
	if key == 'z': 
		rotateZ = rotateZ + angle
	if key == 'Z':
		rotateZ = rotateZ - angle
	# Wire/Solid mode
	if key == 'm':
		if wireMode and not solidMode:
			wireMode = False
			solidMode = True
		else:
			wireMode = True
			solidMode = False
	# Light
	if key == 'l':
		if light:
			light = False
		else:
			light = True
	# Shade
	if key == 'h':
		if shade:
			shade = False
		else:
			shade = True
	global sceneWidht, sceneHeight
	# Orthogonal-Projection
	if key == 'o':
		if perspectiveMode:
			orthoMode = True
			perspectiveMode =False
			resizeViewport(sceneWidth, sceneHeight)
    # Perspective-Projection
	if key == 'p':
		if orthoMode:
			orthoMode = False
			perspectiveMode =True
			resizeViewport(sceneWidth, sceneHeight)
	glutPostRedisplay()

# Adjust projection matrix to window size
def resizeViewport(width, height):
	global sceneWidth, sceneHeight, fov, near, far
	if height == 0:
		height = 1
	sceneWidth = width
	sceneHeight = height
	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()
	# set Viewport
	glViewport(0, 0, int(width), int(height))
	aspect = float(width)/ height
	aspectHeight = float(height) / width
	# Ortho Projection
	if orthoMode:
		if width == height:
			glOrtho(-1.5 + zoomFactor, 1.5 - zoomFactor, -1.5 + zoomFactor, 1.5 - zoomFactor, -10.0, 10.0)
		elif width <= height:
			glOrtho(-1.5 + zoomFactor , 1.5 - zoomFactor, (-1.5 + zoomFactor) * aspectHeight, (1.5 - zoomFactor) * aspectHeight, -1.0, 1.0)
		else:
			glOrtho((-1.5 + zoomFactor)* aspect, (1.5 - zoomFactor) * aspect, -1.5 + zoomFactor, 1.5 - zoomFactor, -10.0, 10.0)
	# Perspective Projection
	if perspectiveMode:
		if width <= height:
			gluPerspective(fov*aspectHeight, aspect, near, far)
		else:
			gluPerspective(fov, aspect, near, far)
		gluLookAt(0, 0, 3 + zoomFactor, 0, 0 ,0 , 0 ,1 ,0)    
	glMatrixMode(GL_MODELVIEW)

# Render
def display():
	global scaleFactor, center, my_vbo, actOri, angle, axis, data, wireMode, solidMode, light, newXPos, newYPos, shade, lightPosition
	glMatrixMode(GL_MODELVIEW)
	# Clear framebuffer
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
	# Reset modelview matrix
	glLoadIdentity()
	# Light
	if light:
		glEnable(GL_LIGHTING)
		glLightfv(GL_LIGHT0, GL_POSITION, lightPosition)
		glEnable(GL_LIGHT0)
		# Possibility to change color
		glEnable(GL_COLOR_MATERIAL)
		glEnable(GL_DEPTH_TEST)
		glEnable(GL_NORMALIZE)
	else:
		glDisable(GL_LIGHTING)
	# render vertox buffer object
	my_vbo.bind()
	glEnableClientState(GL_VERTEX_ARRAY)
	glEnableClientState(GL_NORMAL_ARRAY)
	glVertexPointer(3, GL_FLOAT, 24 , my_vbo)
	glNormalPointer(GL_FLOAT, 24 , my_vbo + 12)
	# Translate
	glTranslate(newXPos,newYPos,0.0)
	# Rotate
	#glRotate(rotateX, 1, 0, 0)
	#glRotate(rotateY, 0, 1, 0)
	#glRotate(rotateZ, 0, 0, 1)
	
	###
	glMultMatrixf(actOri*rotate(angle, axis))
	
	# Scale
	glScale(scaleFactor, scaleFactor, scaleFactor)
	# move to center
	glTranslate(-center[0], -center[1], -center[2])
	
	
	# show object as wires
	#glTranslatef(0.0, -boundingBox[0][1], 0.0)
	if wireMode:
		glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
		# Draw VBO as Triangles
		glDrawArrays(GL_TRIANGLES, 0, len(data))
	# show object as solid
	if solidMode:
		glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
		# Draw VBO as Triangles
		glDrawArrays(GL_TRIANGLES, 0, len(data))
	#glTranslatef(0.0, boundingBox[0][1], 0.0)
	if shade:
		xLight = lightPosition[0]
		yLight = lightPosition[1]
		zLight = lightPosition[2]
		shadowColor = [0.05,0.05,0.05]
		if yLight != 0.:
			p = [1.0, 0, 0, 0, 0, 1.0, 0, -1.0/yLight, 0, 0, 1.0, 0, 0, 0, 0, 0]
		else:
			p = [1.0, 0, 0, 0, 0, 1.0, 0, -1.0/0.1, 0, 0, 1.0, 0, 0, 0, 0, 0]
		#glColor3fv(modelColor)
		# render object normally
		##glCallList(my_vbo)
		# use modelview matrix
		glMatrixMode(GL_MODELVIEW)
		# save state
		glTranslatef(0.0, boundingBox[0][1], 0.0)
		glPushMatrix()
		# translate back
		glTranslatef(xLight, yLight, zLight)
		# project object
		glMultMatrixf(p)
		# move light to origin
		glTranslatef(-xLight, -yLight, -zLight)
		glDisable(GL_LIGHTING)
		##glScale(scaleFactor,scaleFactor,scaleFactor)
		##glTranslate(-center[0],center[1],center[2])
		glColor3fv(shadowColor)
		glTranslatef(0.0, -boundingBox[0][1], 0.0)
		#print boundingBox[0][1]
		glDrawArrays(GL_TRIANGLES,0,len(data))
		
		glColor3fv(modelColor)
		##glDisable(GL_LIGHTING)
		##glColor3fv(shadowColor)
		##glCallList(my_vbo)
		glPopMatrix()
		glEnable(GL_LIGHTING)
		
	my_vbo.unbind()
	glDisableClientState(GL_VERTEX_ARRAY)
	glDisableClientState(GL_NORMAL_ARRAY)
	#swap buffer
	glutSwapBuffers() 

def rotate(angle, axis):
	c,mc = cos(angle), 1-cos(angle)
	s = sin(angle)
	l = sqrt(dot(array(axis), array(axis)))
	x,y,z = array(axis)/l
	
	r = matrix(
		[ [x*x*mc+c, x*y*mc-z*s, x*z*mc+y*s, 0],
		  [x*y*mc+z*s, y*y*mc+c, y*z*mc-x*s, 0],
		  [x*z*mc-y*s, y*z*mc+x*s, z*z*mc+c, 0],
		  [0,0,0,1] ]
	)
	return r.transpose()

def projectOnSphere(x, y, r):
	x,y = x-WIDTH/2.0, HEIGHT/2.0-y
	a = min(r*r, x*x, y*y)
	z = sqrt(r*r-a)
	l = sqrt(x*x+y*y+z*z)
	return x/l, y/l, z/l

# Init Window, register Callback functions, init geometry, start processing
def main():
	glutInit(sys.argv)
	glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
	glutInitWindowSize (500,500)
	glutCreateWindow("OpenGL obj Viewer")
	# Register display callback function
	glutDisplayFunc(display)
	# Register reshape callback function
	glutReshapeFunc(resizeViewport)
	# Register keyboad callback function
	glutKeyboardFunc(keyPressed)
	#register mouse function
	glutMouseFunc(mouse)
	# Register motion function
	glutMotionFunc(mouseMotion)
	# Init Geometry
	initGeometryFromObjFile()
	# Init OpenGL context
	initGL(500,500)
	# Start even processing
	glutMainLoop()


if __name__ == '__main__':
	main()

