from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
from OpenGL.arrays import vbo
from numpy import *
import sys, math, os
from pandas.core import reshape

EXIT = -1
FIRST = 0
backOrFront = 0
doRotation = False
angle = 10
wire = True
translation = False
zoom = False
shadow = False
orthogonal = True
zoomFactor = 0
newXPos = 0.0
newYPos = 0.0

light = False

mouseLastX = None
mouseLastY = None

WIDTH, HEIGTH = 500, 500
aspect = float(WIDTH/HEIGTH)
fov = 45.0
near = 0.1
far = 100.0

angle = 0
actOri = matrix([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
axis = [1., 0., 0.]

MAXZOOM = 1.5
MINZOOM = -10.0

CAMERA_Z = 4
PLANE = 1.5

# color definitions
black = (0.0, 0.0, 0.0, 0.0)
white = (1.0, 1.0, 1.0, 1.0)
blue = (0.0, 0.0, 1.0, 0.0)
green = (0.0, 1.0, 0.0, 0.0)
yellow = (1.0, 1.0, 0.0, 0.0)
red = (1.0, 0.0, 0.0, 0.0)

startP = (0.0, 0.0)

lightX = 0.01
lightY = 20
lightZ = 0.01

#modelList = []

def init(width, heigth):
   """ Initialize an OpenGL window """
   global modelList
   glClearColor(white[0], white[1], white[2], 0.0)         #background color
   glColor(blue)
   glMatrixMode(GL_PROJECTION)              #switch to projection matrix
   glLoadIdentity()                         #set to 1
   glOrtho(-1.5, 1.5, -1.5, 1.5, -1.0, 1.0) #multiply with new p-matrix
   glMatrixMode(GL_MODELVIEW)               #switch to modelview matrix


def reshape(width, heigth):
   """ adjust projection matrix to window size"""
   global zoomFactor, orthogonal, fov, near, far

   #HIER WEITER MACHEN!
   aspect = float(width) / heigth
   aspectHeigth = float(heigth) / width

   glViewport(0, 0, width, heigth)
   glMatrixMode(GL_PROJECTION)
   glLoadIdentity()
   if orthogonal:
       if width == heigth:
           glOrtho(-1.5 + zoomFactor, 1.5 - zoomFactor, -1.5 + zoomFactor, 1.5 - zoomFactor, -1.0, 1.0)
       elif width <= heigth:
           glOrtho(-1.5 + zoomFactor, 1.5 - zoomFactor, (-1.5 + zoomFactor) * aspectHeigth,
                   (1.5 - zoomFactor) * aspectHeigth, -1.0, 1.0)
       else:
           glOrtho((-1.5 + zoomFactor) * aspect, (1.5 - zoomFactor) * aspect, -1.5 + zoomFactor, 1.5 - zoomFactor,
                   -1.0, 1.0)
   else:
       if width <= heigth:
           gluPerspective(fov * aspectHeigth, aspect, near, far)
       else:
           gluPerspective(fov, aspect, near, far)
       gluLookAt(0, 0, 3 + zoomFactor, 0, 0, 0, 0, 1, 0)


   glMatrixMode(GL_MODELVIEW)


def keyPressed(key, x, y):
   """ handle keypress events """
   global backOrFront, wire, orthogonal, WIDTH, HEIGTH, shadow, lightX, light

   if (key == 'K' or key == 'k'):
       backOrFront = 0
   elif (key == 'L' or key == 'l'):
       backOrFront = 1

   if key == chr(27): # chr(27) = ESCAPE
       sys.exit()
   if (key == 'S' or key == 's'):
       if backOrFront == 0:
         glColor(black)
       else:
         glClearColor(black[0], black[1], black[2], 1.0)
   if (key == 'W' or key == 'w'):
       if backOrFront == 0:
         glColor(white)
       else:
         glClearColor(white[0], white[1], white[2], 1.0)
   if (key == 'B' or key == 'b'):
       if backOrFront == 0:
           glColor(blue)
       else:
           glClearColor(blue[0], blue[1], blue[2], 1.0)
   if (key == 'R' or key == 'r'):
       if backOrFront == 0:
           glColor(red)  # render stuff
       else:
           glClearColor(red[0], red[1], red[2], 1.0)
   if (key == 'G' or key == 'g'):
       if backOrFront == 0:
           glColor(yellow)
       else:
           glClearColor(yellow[0], yellow[1], yellow[2], 1.0)
   if (key == 'P' or key == 'p'):
       wire = not wire
   if (key == 'O' or key == 'o'):
       orthogonal = not orthogonal
       reshape(WIDTH, HEIGTH)
   if (key == 'H' or key == 'h'):
       shadow = not shadow
   if (key == 'Z' or key == 'z'):
       light = not light


   glutPostRedisplay()


def rotate(angle, axis):
    c, mc = cos(angle), 1-cos(angle)
    s = sin(angle)
    l = sqrt(dot(array(axis), array(axis)))
    x, y, z = array(axis) / l
    r = matrix(
        [[x*x*mc+c, x*y*mc-z*s, x*z*mc+y*s, 0],
         [x*y*mc+z*s, y*y*mc+c, y*z*mc-x*s, 0],
         [x*z*mc-y*s, y*z*mc+x*s, z*z*mc+c, 0],
         [0, 0, 0, 1]])
    return r.transpose()


def projectOnSphere(x, y, r):
    x, y = x - WIDTH/2.0, HEIGTH/2.0 - y
    a = min(r*r, x*x, y*y)
    z = sqrt(r*r - a)
    l = sqrt(x*x + y*y + z*z)
    return x/l, y/l, z/l


def mouse(button, state, x, y):
   global doRotation, WIDTH, HEIGTH, translation, mouseLastX, mouseLastY, zoom, startP, actOri, angle, axis

   mouseLastX, mouseLastY = None, None

   """ handle mouse events """
   r = min(WIDTH,HEIGTH)/2.0
   if button == GLUT_LEFT_BUTTON:
       if state == GLUT_DOWN:
           doRotation = True
           startP = projectOnSphere(x,y,r)
       elif state == GLUT_UP:
           doRotation = False
           actOri = actOri * rotate(angle, axis)
           angle = 0

   if button == GLUT_RIGHT_BUTTON:
       if state == GLUT_DOWN:
           translation = True
       if state == GLUT_UP:
           translation = False

   if button == GLUT_MIDDLE_BUTTON:
       if state == GLUT_DOWN:
           zoom = True
       if state == GLUT_UP:
           zoom = False


def mouseMotion(x,y):
   global WIDTH, HEIGth, angle, scale, startP, axis, translation, zoom, zoomFactor
   global mouseLastX, mouseLastY, newXPos, newYPos

   xDiff = 0
   yDiff = 0

   # calc difference between act and last x,y mouse coordinates
   if mouseLastX != None:
       xDiff = x - mouseLastX
   if mouseLastY != None:
       yDiff = y - mouseLastY

   if doRotation:
       r = min(WIDTH, HEIGTH) / 2.0
       moveP = projectOnSphere(x,y,r)
       angle = math.acos(dot(startP, moveP))
       axis = cross(startP, moveP)

   if zoom:
       if mouseLastY < y:
           zoomFactor += 0.01
           if zoomFactor >= MAXZOOM:
               zoomFactor = MAXZOOM - 0.01
           if zoomFactor <= MINZOOM:
               zoomFactor = MINZOOM

       if mouseLastY > y:
           zoomFactor -= 0.01
           if zoomFactor >= MAXZOOM:
               zoomFactor = MAXZOOM - 0.01
           if zoomFactor <= MINZOOM:
               zoomFactor = MINZOOM
       reshape(WIDTH, HEIGTH)

   if translation:
       transScale = float(WIDTH) / 2.0
       if xDiff != 0:
           newXPos += xDiff / transScale
       if yDiff != 0:
           newYPos += -yDiff / transScale

   # Remember last x,y mouse coordinates
   mouseLastX = x
   mouseLastY = y
   glutPostRedisplay()


def menu_func(value):
   """ handle menue selection """
   print "menue entry ", value, "choosen..."
   if value == EXIT:
       sys.exit()
   glutPostRedisplay()


def loadObj(filename):
   oVertices = []
   oNormales = []
   oFaces = []

   for line in file(filename):
      if line.split():
         check = line.split()[0]
         if check == 'v':
            oVertices.append(map(float, line.split()[1:]))
         if check == 'vn':
            oNormales.append(map(float, line.split()[1:]))
         if check == 'f':
            faces = line.split()[1:]
            for face in faces:
               oFaces.append(map(float, face.split('//')))

   for face in oFaces:
      if len(face) == 1:
         face.insert(1, 1.0)
         face.insert(2, 1.0)
      if len(face) == 2:
         face.insert(1, 1.0)

   return oVertices, oNormales, oFaces


def display():
    global vbo, scale, data, actOri, angle, axis, wire, lightX, lightY, lightZ

    # Clear framebuffer
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Reset modelview matrix
    glLoadIdentity()

    if light:
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_NORMALIZE)
        glLightfv(GL_LIGHT0, GL_POSITION, [lightX, lightY, lightZ])
    else:
        glDisable(GL_LIGHTING)


    vbo.bind()
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_NORMAL_ARRAY)

    glVertexPointer(3, GL_FLOAT, 24, vbo)
    glNormalPointer(GL_FLOAT, 24, vbo + 12)

    glLoadIdentity()
    # Translate
    glTranslate(newXPos,newYPos,0.0)
    glMultMatrixf(actOri * rotate(angle, axis))

    # Scale
    glScale(scale, scale, scale)
    glTranslatef(-center[0], -center[1], -center[2])  # move to center
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_NORMALIZE)
    #glShadeModel(GL_FLAT)
    #reshape(WIDTH, HEIGTH)


    #if shadow:
        #print "Schatten!"
        #calcShadow()
    #else:
        #print "Kein Schatten!"
        #glDisable(GL_LIGHTING)
        #glDisable(GL_DEPTH_TEST)
        #glDisable(GL_LIGHTING)
        #glDisable(GL_LIGHT0)

    if wire:
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glDrawArrays(GL_TRIANGLES, 0, len(data))
    else:
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glDrawArrays(GL_TRIANGLES, 0, len(data))


    vbo.unbind()

    glDisableClientState(GL_VERTEX_ARRAY)
    glDisableClientState(GL_NORMAL_ARRAY)

    glutSwapBuffers()            #swap buffer

def calcShadow():
    global lightX, lightY, lightZ#, modelList

    #glCallList(modelList)
    p = matrix([[1.0, 0, 0, 0], [0, 1.0, 0, 0], [0, 0, 1.0, 0], [0, -1/lightY, 0, 0]]).transpose()
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glTranslatef(lightX, lightY, lightZ)
    glMultMatrixf(p)
    glTranslatef(-lightX, -lightY, -lightZ)
    glColor3f(0.15, 0.15, 0.15)
    #glCallList(modelList)
    glPopMatrix()





def initGeometryFromObjFile():
    '''
    load obj File, init Bounding Box, init Faces
    '''
    global vbo, scale, center, data

    # check parameters
    if len(sys.argv) == 1:
        print "python oglViewer.py objectFile.obj"
        sys.exit(-1)

    print "Used File: ", sys.argv[1]

    # load obj File
    objectVertices, objectNormals, objectFaces = loadOBJ(sys.argv[1])
    data = []

    # Create BoundingBox
    boundingBox = [map(min, zip(*objectVertices)), map(max, zip(*objectVertices))]
    # Calc center of bounding box
    center = [(x[0] + x[1]) / 2.0 for x in zip(*boundingBox)]
    # Calc scale factor
    scale = 2.0 / max([(x[1] - x[0]) for x in zip(*boundingBox)])

    # get the right data for the vbo
    for vertex in objectFaces:
        vn = int(vertex[0]) - 1
        nn = int(vertex[2]) - 1
        if objectNormals:
            data.append(objectVertices[vn] + objectNormals[nn])
        else:
            # calc standard normals, if no objectNormals available
            normals = [x - y for x, y in zip(objectVertices[vn], center)]
            l = math.sqrt(normals[0] ** 2 + normals[1] ** 2 + normals[2] ** 2)
            normals = [x / l for x in normals]
            data.append(objectVertices[vn] + normals)

    vbo = vbo.VBO(array(data, 'f'))


def loadOBJ(filename):
    '''
    Load .obj File and return three lists with object-vertices, object-normals and object-faces
    '''
    objectVertices = []
    objectNormals = []
    objectFaces = []
    data = []

    for lines in file(filename):
        # check if not empty
        if lines.split():
            check = lines.split()[0]
            if check == 'v':
                objectVertices.append(map(float, lines.split()[1:]))
            if check == 'vn':
                objectNormals.append(map(float, lines.split()[1:]))
            if check == 'f':
                first = lines.split()[1:]
                for face in first:
                    objectFaces.append(map(float, face.split('//')))

    for face in objectFaces:
        # if no vt is available fill up with 0 at list position 1
        if len(face) == 2:
            face.insert(1, 0.0)
        # if no vt and no vn is available fill up with 0 at list position 1 and 2
        if len(face) == 1:
            face.insert(1, 0.0)
            face.insert(2, 0.0)

    return objectVertices, objectNormals, objectFaces

def main():
   global WIDTH, HEIGTH
   # Hack for Mac OS X
   cwd = os.getcwd()
   glutInit(sys.argv)
   os.chdir(cwd)

   glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
   glutInitWindowSize(WIDTH, HEIGTH)
   glutCreateWindow("simple openGL/GLUT template")

   glutDisplayFunc(display)     #register display function
   glutReshapeFunc(reshape)     #register reshape function
   glutKeyboardFunc(keyPressed) #register keyboard function 
   glutMouseFunc(mouse)         #register mouse function
   glutMotionFunc(mouseMotion)  #register motion function
   glutCreateMenu(menu_func)    #register menue function

   initGeometryFromObjFile()
   init(WIDTH,HEIGTH) #initialize OpenGL state

   glutMainLoop() #start even processing


if __name__ == "__main__":
   main()