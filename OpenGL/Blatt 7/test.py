'''
Created on May 23, 2013
Finished on Jun 01, 2013
Generative Computergrafik, Uebungsblatt 7, Aufgabe 1
OpenGL obj Viewer - Bewertete Abgabe
Hochschule RheinMain, Medieninformatik
@author: Soeren Kroell
Start des Programms mit:
- python objectFile.obj
Standardwerte:
- Objektdarstellung als wire 
- Intrinsische Kamera auf orthographische Projektion
Folgende Tastaturbelegungen sind enthalten:
- b:    Aendern der Hintergrundfarbe
- f:    Aendern der Vordergrundfabre
- o:    Umstellen der intrinsischen Kamera auf orthographische Projektion
- p:    Umstellen der intrinsischen Kamera auf perspektivische Projektion
- x:    im Uhrzeigersinn um die x-Achse zu drehen
- X:    gegen den Uhrzeigersinn um die x-Achse zu drehen
- y:    im Uhrzeigersinn um die y-Achse zu drehen
- Y:    gegen den Uhrzeigersinn um die y-Achse zu drehen
- z:    im Uhrzeigersinn um die z-Achse zu drehen
- Z:    gegen den Uhrzeigersinn um die z-Achse zu drehen
- w:    Objekt als Polygonnetz darstellen
- s:    Objekt ausgefuellt anzeigen
- l:    Licht einschalten
- k:    Licht ausschalten
- ESC:  Frame schliessen und Programm beenden 
Folgende Mausbelegungen sind enthalten:
- linke Muastaste:       Objekt rotieren
- Mittlere Maustaste:    Objekt zoom
- Rechte Maustaste:      Objekt verschieben
'''

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.arrays import vbo
from numpy import array

import numpy, math

# Define globals
my_vbo = None

doZoom = False
doRotation = False
doTranslation = False
solidMode = False
wireMode = True
orthoMode = True
perspectiveMode = False
light = False

mouseLastX = None
mouseLastY = None

angle = 10
newXPos = 0.0
newYPos = 0.0
zoomFactor = 0

frontColorIndex, backColorIndex = 2, 1
rotateX, rotateY, rotateZ = 0, 0, 0
WIDTH, HEIGHT = 500, 500
MAX_ZOOM = 1.5
MIN_ZOOM = -10.0

aspect = float(WIDTH / HEIGHT)
FOV = 50.0
NEAR_PLANE = 0.1
FAR_PLANE = 100.0

rotateX, rotateY, rotateZ = 0, 0, 0

# color definitions
colorList = [(0.0, 0.0, 0.0, 0.0),  # black
             (1.0, 1.0, 1.0, 1.0),  # white
             (1.0, 0.0, 0.0, 0.0),  # red
             (0.0, 1.0, 0.0, 0.0),  # green
             (0.0, 0.0, 1.0, 0.0),  # blue
             (1.0, 1.0, 0.0, 0.0)]  # yellow


def initGL(width, height):
    '''
    OpenGL initialize
    '''
    # Set background color - black
    glClearColor(colorList[0][0], colorList[0][1], colorList[0][2], colorList[0][3])
    # switch to projection matrix
    glMatrixMode(GL_PROJECTION)
    # set to 1
    glLoadIdentity()
    # Camera, multiply with new p-matrix
    glOrtho(-1.5, 1.5, -1.5, 1.5, -10.0, 10.0)
    # switch to modelview matrix
    glMatrixMode(GL_MODELVIEW)


def initGeometryFromObjFile():
    '''
    load obj File, init Bounding Box, init Faces
    '''
    global my_vbo, scaleFactor, center, data

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
    scaleFactor = 2.0 / max([(x[1] - x[0]) for x in zip(*boundingBox)])

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

    my_vbo = vbo.VBO(array(data, 'f'))


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


def mouse(button, state, x, y):
    '''
    handle mouse events
    '''
    global doRotation, doZoom, doRotation, doTranslation, mouseLastX, mouseLastY

    mouseLastX, mouseLastY = None, None

    # rotate object
    if button == GLUT_LEFT_BUTTON:
        if state == GLUT_DOWN:
            doRotation = True
        if state == GLUT_UP:
            doRotation = False

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
    ''' 
    handle mouse motion
    '''
    global angle, doZoom, doRotation, doTranslation, scaleFactor, center, mouseLastX, mouseLastY, rotateX, rotateY, sceneWidth, sceneHeight, newXPos, newYPos, zoomFactor

    xDiff = 0
    yDiff = 0

    # calc difference between act and last x,y mouse coordinates
    if mouseLastX != None:
        xDiff = x - mouseLastX
    if mouseLastY != None:
        yDiff = y - mouseLastY

    # rotate
    if doRotation:
        if xDiff != 0:
            rotateY += xDiff
        if yDiff != 0:
            rotateX += yDiff

    # zoom  
    if doZoom:
        zScale = float(sceneHeight) / angle
        if yDiff != 0:
            zoomFactor += yDiff / zScale
            # limit zoomFactor
            if zoomFactor >= MAX_ZOOM:
                zoomFactor = MAX_ZOOM - 0.01
            if zoomFactor <= MIN_ZOOM:
                zoomFactor = MIN_ZOOM
            reshape(sceneWidth, sceneHeight)

            # translatation
    if doTranslation:
        scale = float(sceneWidth) / 2.0
        if xDiff != 0:
            newXPos += xDiff / scale
        if yDiff != 0:
            newYPos += -yDiff / scale

    # Remember last x,y mouse coordinates
    mouseLastX = x
    mouseLastY = y

    glutPostRedisplay()


def keyPressed(key, x, y):
    '''
    Handle keypress events
    '''
    global colorList, frontColorIndex, backColorIndex, rotateX, rotateY, rotateZ, perspectiveMode, orthoMode, solidMode, gridMode, light

    # If escape is pressed, kill everything.
    if key == '\x1b':
        sys.exit()

    # Change background color
    if key == 'b':
        if backColorIndex < len(colorList):
            glClearColor(colorList[backColorIndex][0], colorList[backColorIndex][1], colorList[backColorIndex][2],
                         colorList[backColorIndex][3])
            backColorIndex += 1
        else:
            backColorIndex = 1
            glClearColor(colorList[0][0], colorList[0][1], colorList[0][2], colorList[0][3])

    # Change foreground color / object color
    if key == 'f':
        if frontColorIndex < len(colorList):
            glColor(colorList[frontColorIndex][0], colorList[frontColorIndex][1], colorList[frontColorIndex][2])
            frontColorIndex += 1
        else:
            frontColorIndex = 1
            glColor(colorList[0][0], colorList[0][1], colorList[0][2])

    # Rotate with keys x,X,y,Y,z,Z
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

    # Show Object in WireMode
    if key == 'w':
        wireMode = True
        solidMode = False

    # Show Object in SolidMode
    if key == 's':
        solidMode = True
        wireMode = False

    # Turn on light
    if key == 'l':
        light = True

    # Turn off light
    if key == 'k':
        light = False

    global sceneWidht, sceneHeight
    # Activate Orthogonal-Projection
    if key == 'o':
        if perspectiveMode:
            orthoMode = True
            perspectiveMode = False
            reshape(sceneWidth, sceneHeight)

    # Activate Perspective-Projection
    if key == 'p':
        if orthoMode:
            orthoMode = False
            perspectiveMode = True
            reshape(sceneWidth, sceneHeight)

    glutPostRedisplay()


def reshape(width, height):
    '''
    Adjust projection matrix to window size
    '''
    global sceneWidth, sceneHeight, orthoMode, perspectiveMode, zoomFactor

    if height == 0:
        height = 1

    # remember widht, height
    sceneWidth = width
    sceneHeight = height

    # Change Matrix Mode
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    # set Viewport
    glViewport(0, 0, int(width), int(height))

    aspectWidth = float(width) / height
    aspectHeight = float(height) / width

    # Ortho Projection
    if orthoMode:
        if width == height:
            glOrtho(-1.5 + zoomFactor, 1.5 - zoomFactor, -1.5 + zoomFactor, 1.5 - zoomFactor, -10.0, 10.0)
        elif width <= height:
            glOrtho(-1.5 + zoomFactor, 1.5 - zoomFactor, (-1.5 + zoomFactor) * aspectHeight,
                    (1.5 - zoomFactor) * aspectHeight, -1.0, 1.0)
        else:
            glOrtho((-1.5 + zoomFactor) * aspectWidth, (1.5 - zoomFactor) * aspectWidth, -1.5 + zoomFactor,
                    1.5 - zoomFactor, -10.0, 10.0)

    # Perspective Projection
    if perspectiveMode:
        if width <= height:
            gluPerspective(FOV * aspectHeight, aspectWidth, NEAR_PLANE, FAR_PLANE)
        else:
            gluPerspective(FOV, aspectWidth, NEAR_PLANE, FAR_PLANE)
        gluLookAt(0, 0, 3 - zoomFactor, 0, 0, 0, 0, 1, 0)

    glMatrixMode(GL_MODELVIEW)


def display():
    '''
    Render all objects
    '''
    global scaleFactor, center, my_vbo, actOri, angle, axis, data, wireMode, orthoMode, perspectiveMode, solidMode, light, newXPos, newYPos, zoomFactor

    # Clear framebuffer
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Reset modelview matrix
    glLoadIdentity()

    # if light is enabled
    if light:
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_NORMALIZE)
    else:
        glDisable(GL_LIGHTING)

    # render vertox buffer object
    my_vbo.bind()

    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_NORMAL_ARRAY)

    glVertexPointer(3, GL_FLOAT, 24, my_vbo)
    glNormalPointer(GL_FLOAT, 24, my_vbo + 12)

    # Translate
    glTranslate(newXPos, newYPos, 0.0)

    # Rotate
    glRotate(rotateX, 1, 0, 0)
    glRotate(rotateY, 0, 1, 0)
    glRotate(rotateZ, 0, 0, 1)

    # Scale
    glScale(scaleFactor, scaleFactor, scaleFactor)

    # move to center
    glTranslate(-center[0], -center[1], -center[2])

    # show object as wires
    if wireMode:
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        # Draw VBO as Triangles
        glDrawArrays(GL_TRIANGLES, 0, len(data))

    # show object as solid
    if solidMode:
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        # Draw VBO as Triangles
        glDrawArrays(GL_TRIANGLES, 0, len(data))

    my_vbo.unbind()

    glDisableClientState(GL_VERTEX_ARRAY)
    glDisableClientState(GL_NORMAL_ARRAY)

    # swap buffer
    glutSwapBuffers()


def main():
    '''
    Init Window, register Callback functions, init geometry, start processing
    '''
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(500, 500)
    glutCreateWindow("OpenGL obj Viewer")

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
    # Init Geometry
    initGeometryFromObjFile()

    # Init OpenGL context
    initGL(500, 500)

    # Start even processing
    glutMainLoop()


if __name__ == '__main__':
    main()