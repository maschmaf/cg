"""
    Escape:
        Viewer beenden
    w,s,r,g,b:
        Modellfarbe aendern
    W,S,R,G,B:
        Hintergrundfarbe aendern
    o/O:
        Wechseln zwischen Wireframe und Oberflaeche
    p/P:
        Wechsel zwischen Orthogonal- und Zentral-Projektion
    h/H:
        Licht ein- und ausschalten (Schatten funktioniert nicht)
"""

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.arrays import vbo
from numpy import *
from math import *

# Define globals
doZoom = False
doRotation = False
doTranslation = False
wire = False
orthoMode = True
light = False

mouseLastX = None
mouseLastY = None

angle = 0
newXPos = 0.0
newYPos = 0.0
zoomFactor = 0

WIDTH, HEIGHT = 500, 500
MAX_ZOOM = 1.5
MIN_ZOOM = -10.0

aspect = float(WIDTH / HEIGHT)
FOV = 50.0
NEAR = 0.1
FAR = 100.0

lightPos = [0, 20, 0]

startP = ()

actOri = matrix([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
axis = [1., 0., 0.]


# color definitions
BLACK = (0.0, 0.0, 0.0, 0.0)
WHITE = (1.0, 1.0, 1.0, 1.0)
BLUE = (0.0, 0.0, 1.0, 0.0)
GREEN = (0.0, 1.0, 0.0, 0.0)
YELLOW = (1.0, 1.0, 0.0, 0.0)
RED = (1.0, 0.0, 0.0, 0.0)
SHADOW_COLOR = (0.15, 0.15, 0.15, 0.0)

camX = 0.0
camY = 0.0
camZ = 0.0

def initGL(width, height):
    """ Initialize an OpenGL window """
    # Set colors
    glColor(RED)
    glClearColor(BLUE[0], BLUE[1], BLUE[2], BLUE[3])

    # switch to projection matrix
    glMatrixMode(GL_PROJECTION)
    # set to 1
    glLoadIdentity()
    # Camera, multiply with new p-matrix
    glOrtho(-1.5, 1.5, -1.5, 1.5, -1.0, 1.0)
    # switch to modelview matrix
    glMatrixMode(GL_MODELVIEW)


def createVBO():
    global vbo, scaleFactor, center, data, boundingBox

    # load obj File
    objectVertices, objectNormals, objectFaces = readOBJ(sys.argv[1])
    data = []

    # BoundingBox
    boundingBox = [map(min, zip(*objectVertices)), map(max, zip(*objectVertices))]
    # Center BoundingBox
    center = [(x[0] + x[1]) / 2.0 for x in zip(*boundingBox)]
    # Scalefactor
    scaleFactor = 2.0 / max([(x[1] - x[0]) for x in zip(*boundingBox)])

    for vertex in objectFaces:
        v = int(vertex[0]) - 1
        vn = int(vertex[2]) - 1
        if objectNormals:
            data.append(objectVertices[v] + objectNormals[vn])
        else:
            # calc standard normals, if no objectNormals available
            normals = [x - y for x, y in zip(objectVertices[v], center)]
            l = sqrt(normals[0] ** 2 + normals[1] ** 2 + normals[2] ** 2)
            normals = [x / l for x in normals]
            data.append(objectVertices[v] + normals)
    vbo = vbo.VBO(array(data, 'f'))


def readOBJ(filename):
    objectVertices = []
    objectNormals = []
    objectFaces = []

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


def projectOnSphere(x, y, r):
    x, y = x - WIDTH/2.0, HEIGHT/2.0 - y
    a = min(r*r, x*x, y*y)
    z = sqrt(r*r - a)
    l = sqrt(x*x + y*y + z*z)
    return x/l, y/l, z/l


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


def mouse(button, state, x, y):
    ''' handle mouse events '''
    global doRotation, doZoom, doRotation, doTranslation, mouseLastX, mouseLastY, actOri, angle, startP

    mouseLastX, mouseLastY = None, None
    r = min(WIDTH, HEIGHT) / 2.0

    # rotate object
    if button == GLUT_LEFT_BUTTON:
        if state == GLUT_DOWN:
            doRotation = True
            startP = projectOnSphere(x, y, r)
        if state == GLUT_UP:
            doRotation = False
            actOri = actOri * rotate(angle, axis)
            angle = 0

    # translate object
    if button == GLUT_RIGHT_BUTTON:
        if state == GLUT_DOWN:
            doTranslation = True
        if state == GLUT_UP:
            doTranslation = False

    # zoom object
    if button == GLUT_MIDDLE_BUTTON:
        if state == GLUT_DOWN:
            doZoom = True
        if state == GLUT_UP:
            doZoom = False


def mouseMotion(x, y):
    ''' handle mouse motion '''
    global angle, doZoom, doRotation, doTranslation, scaleFactor, center, mouseLastX, mouseLastY, newXPos, newYPos, axis, zoomFactor, camZ

    xDiff = 0
    yDiff = 0

    # calc difference between act and last x,y mouse coordinates
    if mouseLastX != None:
        xDiff = x - mouseLastX
    if mouseLastY != None:
        yDiff = y - mouseLastY


    if doRotation:
        r = min(WIDTH, HEIGHT) / 2.0
        moveP = projectOnSphere(x, y, r)
        angle = acos(dot(startP, moveP))
        axis = cross(startP, moveP)

    if doZoom:
        if mouseLastY < y:
            zoomFactor += 0.01
            if zoomFactor >= MAX_ZOOM:
                zoomFactor = MAX_ZOOM - 0.01
            if zoomFactor <= MIN_ZOOM:
                zoomFactor = MIN_ZOOM

        if mouseLastY > y:
            zoomFactor -= 0.01
            if zoomFactor >= MAX_ZOOM:
                zoomFactor = MAX_ZOOM - 0.01
            if zoomFactor <= MIN_ZOOM:
                zoomFactor = MIN_ZOOM
        camZ = zoomFactor
        reshape(WIDTH, HEIGHT)

    # translatation
    if doTranslation:
        scale = float(WIDTH) / 2.0
        if xDiff != 0:
            newXPos += xDiff / scale
        if yDiff != 0:
            newYPos += -yDiff / scale

    mouseLastX = x
    mouseLastY = y

    glutPostRedisplay()


def keyPressed(key, x, y):
    '''
    Handle keypress events
    '''
    global orthoMode, wire, light

    if key == chr(27):  # chr(27) = ESCAPE
        sys.exit()

    if key == 's':
        glColor(BLACK)
    if key == 'S':
        glClearColor(BLACK[0], BLACK[1], BLACK[2], BLACK[3])
    if key == 'w':
        glColor(WHITE)
    if key == 'W':
        glClearColor(WHITE[0], WHITE[1], WHITE[2], WHITE[3])
    if key == 'b':
        glColor(BLUE)
    if key == 'B':
        glClearColor(BLUE[0], BLUE[1], BLUE[2], BLUE[3])
    if key == 'r':
        glColor(RED)
    if key == 'R':
        glClearColor(RED[0], RED[1], RED[2], RED[3])
    if key == 'g':
        glColor(YELLOW)
    if key == 'G':
        glClearColor(YELLOW[0], YELLOW[1], YELLOW[2], YELLOW[3])
    if (key == 'o' or key == 'O'):
        wire = not wire
    if (key == 'h' or key == 'H'):
        light = not light
    if (key == 'p' or key == 'P'):
        orthoMode = not orthoMode
        if orthoMode:
            print "Orthogonal"
        else:
            print "Zentral"
        reshape(WIDTH, HEIGHT)

    glutPostRedisplay()


def reshape(width, height):
    """ adjust projection matrix to window size"""
    global orthoMode, WIDTH, HEIGHT, NEAR, FAR, camZ, zoomF, center

    # Change Matrix Mode
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    # set Viewport
    glViewport(0, 0, int(WIDTH), int(HEIGHT))

    aspectWidth = float(WIDTH) / HEIGHT
    aspectHeight = float(HEIGHT) / WIDTH

    if orthoMode:
        if width <= height:
            glOrtho(-1.5 + zoomFactor, 1.5 - zoomFactor, (-1.5 + zoomFactor) * aspectHeight,
                    (1.5 - zoomFactor) * aspectHeight, -1.0, 1.0)
        else:
            glOrtho((-1.5 + zoomFactor) * aspectWidth, (1.5 - zoomFactor) * aspectWidth, -1.5 + zoomFactor,
                    1.5 - zoomFactor, -1.0, 1.0)
    else:
        if width <= height:
            gluPerspective(FOV * aspectHeight, aspectWidth, NEAR, FAR)
        else:
            gluPerspective(FOV, aspectWidth, NEAR, FAR)
        gluLookAt(camX, camY, 3 - camZ, center[0], center[1], center[2], 0, 1, 0)

    glMatrixMode(GL_MODELVIEW)


def display():
    """ Render all objects"""
    global scaleFactor, center, vbo, actOri, angle, axis, data, newXPos, newYPos, lightPos
    global wire, orthoMode, light, boundingBox, lightPos

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
        glLightfv(GL_LIGHT0, GL_POSITION, [lightPos[0], lightPos[1], lightPos[2], 1.0])
        glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)

        #glPushMatrix()
        #glDisable(GL_LIGHTING)
        #glDisable(GL_DEPTH_TEST)
        #glTranslatef(0.0, -boundingBox[0][1], 0.0)
        #p = matrix([[1.0, 0, 0, 0], [0, 1.0, 0, 0], [0, 0, 1.0, 0], [0, -1 / lightPos[1], 0, 0]])
        ##p = [1.0, 0, 0, 0, 0, 1.0, 0, -1.0 / lightPos[1], 0, 0, 1.0, 0, 0, 0, 0, 0]
        #glTranslatef(lightPos[0], lightPos[1], lightPos[2])
        #glMultMatrixf(p)
        #glTranslatef(-lightPos[0], -lightPos[1], -lightPos[2])
        #glColor3f(SHADOW_COLOR[0], SHADOW_COLOR[1], SHADOW_COLOR[2])
        #glTranslate(0.0, boundingBox[0][1], 0.0)
        #glPopMatrix()
    else:
        glDisable(GL_LIGHTING)
        glDisable(GL_LIGHT0)
        glDisable(GL_DEPTH_TEST)

    vbo.bind()

    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_NORMAL_ARRAY)

    glVertexPointer(3, GL_FLOAT, 24, vbo)
    glNormalPointer(GL_FLOAT, 24, vbo + 12)

    # Translate
    glTranslate(newXPos, newYPos, 0.0)
    # Rotate
    glMultMatrixf(actOri * rotate(angle, axis))
    # Scale
    glScale(scaleFactor, scaleFactor, scaleFactor)
    # Translate to center
    glTranslate(-center[0], -center[1], -center[2])

    if wire:
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glDrawArrays(GL_TRIANGLES, 0, len(data))
    else:
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glDrawArrays(GL_TRIANGLES, 0, len(data))

    vbo.unbind()

    glDisableClientState(GL_VERTEX_ARRAY)
    glDisableClientState(GL_NORMAL_ARRAY)

    # swap buffer
    glutSwapBuffers()


def main():
    if len(sys.argv) == 1:
        print "Datei vergessen!"
        sys.exit(-1)

    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WIDTH, HEIGHT)
    glutCreateWindow("simple openGL/GLUT template")

    # Register display callback function
    glutDisplayFunc(display)
    # Register reshape callback function
    glutReshapeFunc(reshape)
    # Register keyboad callback function
    glutKeyboardFunc(keyPressed)
    # register mouse function
    glutMouseFunc(mouse)
    # Register motion function
    glutMotionFunc(mouseMotion)
    # Init OpenGL context
    initGL(WIDTH, HEIGHT)

    createVBO()


    # Start even processing
    glutMainLoop()


if __name__ == '__main__':
    main()