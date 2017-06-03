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
polygon = False
translation = False
zoom = False
orthogonal = True
zoomFactor = 0
newXPos = 0.0
newYPos = 0.0

mouseLastX = None
mouseLastY = None

WIDTH, HEIGHT = 500, 500
aspect = float(WIDTH/HEIGHT)
fov = 45.0
near = 0.1
far = 100.0

angle = 0
actOri = matrix([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
axis = [1., 0., 0.]

MAXZOOM = 1.5
MINZOOM = -1.5

# color definitions
black = (0.0, 0.0, 0.0, 0.0)
white = (1.0, 1.0, 1.0, 1.0)
blue = (0.0, 0.0, 1.0, 0.0)
green = (0.0, 1.0, 0.0, 0.0)
yellow = (1.0, 1.0, 0.0, 0.0)
red = (1.0, 0.0, 0.0, 0.0)

startP = (0.0, 0.0)

def init(width, height):
   """ Initialize an OpenGL window """
   glClearColor(0.0, 0.0, 0.0, 0.0)         #background color
   glMatrixMode(GL_PROJECTION)              #switch to projection matrix
   glLoadIdentity()                         #set to 1
   glOrtho(-1.5, 1.5, -1.5, 1.5, -1.0, 1.0) #multiply with new p-matrix
   glMatrixMode(GL_MODELVIEW)               #switch to modelview matrix


def reshape(width, height):
   """ adjust projection matrix to window size"""
   global zoomFactor, orthogonal, fov, near, far

   #HIER WEITER MACHEN!
   aspect = float(width) / height
   aspectHeight = float(height) / width

   glViewport(0, 0, width, height)
   glMatrixMode(GL_PROJECTION)
   glLoadIdentity()
   if orthogonal:
       if width == height:
           glOrtho(-1.5 + zoomFactor, 1.5 - zoomFactor, -1.5 + zoomFactor, 1.5 - zoomFactor, -1.0, 1.0)
       elif width <= height:
           glOrtho(-1.5 + zoomFactor, 1.5 - zoomFactor, (-1.5 + zoomFactor) * aspectHeight,
                   (1.5 - zoomFactor) * aspectHeight, -1.0, 1.0)
       else:
           glOrtho((-1.5 + zoomFactor) * aspect, (1.5 - zoomFactor) * aspect, -1.5 + zoomFactor, 1.5 - zoomFactor,
                   -1.0, 1.0)
   else:
       if width <= height:
           gluPerspective(fov * aspectHeight, aspect, near, far)
       else:
           gluPerspective(fov, aspect, near, far)
       gluLookAt(0, 0, 3 + zoomFactor, 0, 0, 0, 0, 1, 0)


   glMatrixMode(GL_MODELVIEW)


def keyPressed(key, x, y):
   """ handle keypress events """
   global backOrFront, polygon, orthogonal, WIDTH, HEIGHT

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
       polygon = not polygon
   if (key == 'O' or key == 'o'):
       orthogonal = not orthogonal
       reshape(WIDTH, HEIGHT)
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
    x, y = x - WIDTH/2.0, HEIGHT/2.0 - y
    a = min(r*r, x*x, y*y)
    z = sqrt(r*r - a)
    l = sqrt(x*x + y*y + z*z)
    return x/l, y/l, z/l


def mouse(button, state, x, y):
   global doRotation, WIDTH, HEIGHT, translation, mouseLastX, mouseLastY, zoom, startP, actOri, angle, axis

   mouseLastX, mouseLastY = None, None

   """ handle mouse events """
   r = min(WIDTH,HEIGHT)/2.0
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
   global WIDTH, HEIGHT, angle, scale, startP, axis, translation, zoom, zoomFactor
   global mouseLastX, mouseLastY, newXPos, newYPos

   xDiff = 0
   yDiff = 0

   # calc difference between act and last x,y mouse coordinates
   if mouseLastX != None:
       xDiff = x - mouseLastX
   if mouseLastY != None:
       yDiff = y - mouseLastY

   if doRotation:
       r = min(WIDTH, HEIGHT) / 2.0
       moveP = projectOnSphere(x,y,r)
       angle = math.acos(dot(startP, moveP))
       axis = cross(startP, moveP)

   if zoom:
       if mouseLastY < y:
           #zoomFactor = zoomFactor - 0.1 if zoomFactor > MINZOOM else zoomFactor
           zoomFactor += 0.01
       if mouseLastY > y:
           zoomFactor -= 0.01
           #zoomFactor = zoomFactor + 0.1 if zoomFactor < MINZOOM else zoomFactor
       reshape(WIDTH, HEIGHT)

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
    global vbo, scale, data, actOri, angle, axis, polygon

    glMatrixMode(GL_MODELVIEW)
    # Clear framebuffer
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    #glRectf(-1.0 ,-1.0 ,1.0, 1.0)


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

    if polygon:
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    else:
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

    glDrawArrays(GL_TRIANGLES, 0, len(data))
    vbo.unbind()
    glDisableClientState(GL_VERTEX_ARRAY)
    glDisableClientState(GL_NORMAL_ARRAY)

    glutSwapBuffers()            #swap buffer


def main():
   global vbo, vertices, normals, faces, center, scale, data, WIDTH, HEIGHT
   # Hack for Mac OS X
   cwd = os.getcwd()
   glutInit(sys.argv)
   os.chdir(cwd)

   glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
   glutInitWindowSize(WIDTH, HEIGHT)
   glutCreateWindow("simple openGL/GLUT template")

   glutDisplayFunc(display)     #register display function
   glutReshapeFunc(reshape)     #register reshape function
   glutKeyboardFunc(keyPressed) #register keyboard function 
   glutMouseFunc(mouse)         #register mouse function
   glutMotionFunc(mouseMotion)  #register motion function
   glutCreateMenu(menu_func)    #register menue function


   vertices, normals, faces = loadObj(sys.argv[1])
   data = []
   boundingBox = [map(min, zip(*vertices)), map(max, zip(*vertices))]
   center = [(x[0] + x[1]) / 2.0 for x in zip(*boundingBox)]
   scale = 2.0 / max([(x[1] - x[0]) for x in zip(*boundingBox)])

   for vertex in faces:
       v = int(vertex[0])-1
       vn = int(vertex[2])-1

       if normals:
           data.append(vertices[v] + normals[vn])
       else:
           l = math.sqrt(vertices[v][0]**2 + vertices[v][1]**2 + vertices[v][2]**2)
           norm = [x/l for x in vertices[v]]
           data.append(vertices[v]+norm)

   vbo = vbo.VBO(array(data, 'f'))

   init(WIDTH,HEIGHT) #initialize OpenGL state

   glutMainLoop() #start even processing


if __name__ == "__main__":
   main()