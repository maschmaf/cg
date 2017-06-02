from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
from OpenGL.arrays import vbo
from numpy import array
import sys, math, os

EXIT = -1
FIRST = 0

def init(width, height):
   """ Initialize an OpenGL window """
   glClearColor(0.0, 0.0, 0.0, 0.0)         #background color
   glMatrixMode(GL_PROJECTION)              #switch to projection matrix
   glLoadIdentity()                         #set to 1
   glOrtho(-1.5, 1.5, -1.5, 1.5, -1.0, 1.0) #multiply with new p-matrix
   glMatrixMode(GL_MODELVIEW)               #switch to modelview matrix


def display():
    global vbo, vertices, normals, faces, scale, center, data
    glClear(GL_COLOR_BUFFER_BIT) #clear screen
    glColor(0.0, 0.0, 1.0)       #render stuff
    #glRectf(-1.0 ,-1.0 ,1.0, 1.0)
    glLoadIdentity()

    vbo.bind()
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_NORMAL_ARRAY)

    glVertexPointer(3, GL_FLOAT, 24, vbo)
    glNormalPointer(GL_FLOAT, 24, vbo + 12)

    glScale(scale, scale, scale)
    glTranslate(-center[0], -center[1], -center[2])

    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    glDrawArrays(GL_TRIANGLES, 0, len(data))
    vbo.unbind()
    glDisableClientState(GL_VERTEX_ARRAY)

    glutSwapBuffers()            #swap buffer


def reshape(width, height):
   """ adjust projection matrix to window size"""
   glViewport(0, 0, width, height)
   glMatrixMode(GL_PROJECTION)
   glLoadIdentity()
   if width <= height:
       glOrtho(-1.5, 1.5,
               -1.5*height/width, 1.5*height/width,
               -1.0, 1.0)
   else:
       glOrtho(-1.5*width/height, 1.5*width/height,
               -1.5, 1.5,
               -1.0, 1.0)
   glMatrixMode(GL_MODELVIEW)


def keyPressed(key, x, y):
   """ handle keypress events """
   if key == chr(27): # chr(27) = ESCAPE
       sys.exit()


def mouse(button, state, x, y):
   """ handle mouse events """
   if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
       print "left mouse button pressed at ", x, y


def mouseMotion(x,y):
   """ handle mouse motion """
   print "mouse motion at ", x, y


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

def main():
   global vbo, vertices, normals, faces, center, scale, data
   # Hack for Mac OS X
   cwd = os.getcwd()
   glutInit(sys.argv)
   os.chdir(cwd)

   glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
   glutInitWindowSize(500, 500)
   glutCreateWindow("simple openGL/GLUT template")

   glutDisplayFunc(display)     #register display function
   glutReshapeFunc(reshape)     #register reshape function
   glutKeyboardFunc(keyPressed) #register keyboard function 
   glutMouseFunc(mouse)         #register mouse function
   glutMotionFunc(mouseMotion)  #register motion function
   glutCreateMenu(menu_func)    #register menue function


   vertices, normals, faces = loadObj(sys.argv[1])
   print (faces[0])
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



   glutAddMenuEntry("First Entry",FIRST) #Add a menu entry
   glutAddMenuEntry("EXIT",EXIT)         #Add another menu entry
   glutAttachMenu(GLUT_RIGHT_BUTTON)     #Attach mouse button to menue

   init(500,500) #initialize OpenGL state

   glutMainLoop() #start even processing


if __name__ == "__main__":
   main()