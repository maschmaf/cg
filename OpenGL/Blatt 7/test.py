# -*- coding: utf-8 -*-
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
from OpenGL.arrays import vbo
from numpy import *
from math import *

import sys, os

objects = dict(COW='data/cow.obj', ELEPHANT='data/elephant.obj', BUNNY='data/bunny.obj', SQUIRREL='data/squirrel.obj')

WIDTH, HEIGHT = 500, 500

RED = [1., 0., 0., 0.]
GREEN = [0., 1., 0., 0.]
BLUE = [0., 0., 1., 0.]
YELLOW = [1., 1., 0., 0.]
BLACK = [0., 0., 0., 0.]
WHITE = [1., 1., 1., 1.]

colors = [BLACK, WHITE, RED, GREEN, BLUE, YELLOW]

ROTATION_ANGLE = .1  # angle for keyboard-rotation
X_AXIS = [1., 0., 0.]
Y_AXIS = [0., 1., 0.]
Z_AXIS = [0., 0., 1.]

MAX_ZOOM = 1.5
MIN_ZOOM = 0.5
INIT_ZOOM = 1.0

CAMERA_Z = 4  # position of camera
PLANE = 1.5


## KEYS:
##    ESC:     exit programm
##
##    x, X:    rotate (anti-)clockwise on x-axis
##    y, Y:    rotate (anti-)clockwise on y-axis
##    z, Z:    rotate (anti-)clockwise on z-axis
##    c:       change color of object
##    C:       change backgroundcolor
##    p:       switch between othogonal and central perspective
##
##
## MOUSE CLICK
##
##    left:    rotate object on arcball
##    middle:  zoom in and out
##    right:   move object


def reset():
    global startPoint
    global axis, actOri, angle
    global doRotation, doDrag, doZoom
    global dragX, dragY, zoom
    global central_projection
    global current_bg, current_obj

    central_projection = False
    doRotation, doDrag, doZoom = False, False, False

    # rotation
    angle = 0
    axis = X_AXIS
    actOri = matrix(
        [[1, 0, 0, 0],
         [0, 1, 0, 0],
         [0, 0, 1, 0],
         [0, 0, 0, 1]])

    dragX, dragY = 0, 0

    zoom = INIT_ZOOM

    # colors
    current_bg, current_obj = 5, 2


def init(width, height):
    """ Initialize an OpenGL window """
    glClearColor(*colors[current_bg])  # background color
    updateProjection()


def display():
    """ Render all objects"""
    global scale, center
    global data, vb
    global dragX, dragY, zoom

    glClearColor(*colors[current_bg])  # background color
    glClear(GL_COLOR_BUFFER_BIT)  # clear screen
    glColor(*colors[current_obj])  # object color

    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

    vb.bind()  # load points
    glEnableClientState(GL_VERTEX_ARRAY)
    glVertexPointerf(vb)

    glLoadIdentity()
    gluLookAt(0, 0, CAMERA_Z, 0, 0, 0, 0, 1, 0)  # update camera
    glTranslatef(dragX, dragY, 0)  # move to specific position
    glMultMatrixf(actOri * rotate(angle, axis))  # rotate
    glScale(scale, scale, scale)  # scale so that boundingbox has a length of 2
    glTranslatef(-center[0], -center[1], -center[2])  # move to center

    glDrawArrays(GL_TRIANGLES, 0, len(data))
    vb.unbind()
    glDisableClientState(GL_VERTEX_ARRAY)

    glutSwapBuffers()


def updateProjection():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    if central_projection:
        showCentral(WIDTH, HEIGHT)
    else:
        showOrtho(WIDTH, HEIGHT)
    glMatrixMode(GL_MODELVIEW)


def showCentral(width, height):
    fieldofview = 40 * zoom
    gluPerspective(fieldofview, width / float(height), CAMERA_Z - PLANE, CAMERA_Z + PLANE)


def showOrtho(width, height):
    zoomedPlane = PLANE * zoom

    if width <= height:
        glOrtho(-zoomedPlane, zoomedPlane,
                -zoomedPlane * height / width, zoomedPlane * height / width,
                CAMERA_Z - PLANE, CAMERA_Z + PLANE)
    else:
        glOrtho(-zoomedPlane * width / height, zoomedPlane * width / height,
                -zoomedPlane, zoomedPlane,
                CAMERA_Z - PLANE, CAMERA_Z + PLANE)


def reshape(width, height):
    """ adjust projection matrix to window size"""
    global WIDTH, HEIGHT
    WIDTH, HEIGHT = width, height
    glViewport(0, 0, width, height)
    updateProjection()
    glutPostRedisplay()


def rotate(angle, axis):
    c, mc = cos(angle), 1 - cos(angle)
    s = sin(angle)
    l = sqrt(dot(array(axis), array(axis)))
    x, y, z = array(axis) / l
    r = matrix(
        [[x * x * mc + c, x * y * mc - z * s, x * z * mc + y * s, 0],
         [x * y * mc + z * s, y * y * mc + c, y * z * mc - x * s, 0],
         [x * z * mc - y * s, y * z * mc + x * s, z * z * mc + c, 0],
         [0, 0, 0, 1]])
    return r.transpose()


def projectOnSphere(x, y, r):
    x, y = x - WIDTH / 2.0, HEIGHT / 2.0 - y
    a = min(r * r, x * x, y * y)
    z = sqrt(r * r - a)
    l = sqrt(x * x + y * y + z * z)
    return x / l, y / l, z / l


def keyPressed(key, x, y):
    """ handle keypress events """
    global current_bg, current_obj
    global actOri, central_projection

    if key == chr(27):
        sys.exit()

    if key in 'xXyYzZcCp0':
        # rotation
        if key == 'x':
            actOri = actOri * rotate(ROTATION_ANGLE, X_AXIS)
        if key == 'X':
            actOri = actOri * rotate(-ROTATION_ANGLE, X_AXIS)
        if key == 'y':
            actOri = actOri * rotate(ROTATION_ANGLE, Y_AXIS)
        if key == 'Y':
            actOri = actOri * rotate(-ROTATION_ANGLE, Y_AXIS)
        if key == 'z':
            actOri = actOri * rotate(ROTATION_ANGLE, Z_AXIS)
        if key == 'Z':
            actOri = actOri * rotate(-ROTATION_ANGLE, Z_AXIS)

        # color switch
        if key == 'C':
            current_bg = current_bg + 1 if current_bg < len(colors) - 1 else 0
        if key == 'c':
            current_obj = current_obj + 1 if current_obj < len(colors) - 1 else 0

        # perspective switch
        if key == 'p':
            central_projection = not central_projection
            updateProjection()
        # reset
        if key == '0':
            reset()
            updateProjection()
        glutPostRedisplay()


def mousebuttonpressed(button, state, x, y):
    """ handle mouse events """
    global startPoint, actOri, angle
    global doRotation, doDrag, doZoom

    r = min(WIDTH, HEIGHT) / 2.0

    if button == GLUT_LEFT_BUTTON:
        if state == GLUT_DOWN:
            doRotation = True
            startPoint = projectOnSphere(x, y, r)
        if state == GLUT_UP:
            doRotation = False
            actOri = actOri * rotate(angle, axis)
            angle = 0

    if button == GLUT_RIGHT_BUTTON:
        if state == GLUT_DOWN:
            startPoint = x, y
            doDrag = True
        if state == GLUT_UP:
            doDrag = False

    if button == GLUT_MIDDLE_BUTTON:
        if state == GLUT_DOWN:
            startPoint = y
            doZoom = True
        if state == GLUT_UP:
            doZoom = False


def mousemoved(x, y):
    """ handle mouse motion """
    global startPoint
    global angle, axis, scale
    global dragX, dragY, zoom

    if doRotation:
        r = min(WIDTH, HEIGHT) / 2.0
        movePoint = projectOnSphere(x, y, r)
        angle = acos(dot(startPoint, movePoint))
        axis = cross(startPoint, movePoint)
        glutPostRedisplay()

    if doDrag:
        xBefore, yBefore = startPoint
        dragX = dragX + float(x - xBefore) / float(WIDTH) * 2 * PLANE * zoom
        dragY = dragY - float(y - yBefore) / float(HEIGHT) * 2 * PLANE * zoom
        startPoint = (x, y)
        glutPostRedisplay()

    if doZoom:
        if startPoint < y:
            zoom = zoom - 0.1 if zoom > MIN_ZOOM else zoom
        if startPoint > y:
            zoom = zoom + 0.1 if zoom < MAX_ZOOM else zoom
        startPoint = y
        updateProjection()
        glutPostRedisplay()


def initGeometry():
    global boundingBox, scale, center

    # bounding box
    boundingBox = [map(min, zip(*vertices)), map(max, zip(*vertices))]

    # center of bounding box
    center = [(coords[0] + coords[1]) / 2.0 for coords in zip(*boundingBox)]

    # find longest side and calculate scale (for length = 2.0)
    scale = 2.0 / max([(coords[1] - coords[0]) for coords in zip(*boundingBox)])


def parseObjFile(filex):
    global data, vb, vertices, normals, faces

    geoData = filex.readlines()

    vertices = [map(float, line.split()[1:]) for line in geoData if line.startswith('v ')]
    normals = [line.split()[1:] for line in geoData if line.startswith('vn')]
    faces = [line.split()[1:] for line in geoData if line.startswith('f')]

    data = []
    for face in faces:
        for f in face:
            if '/' in f:
                tmp = [part if part != '' else -1 for part in f.split('/')]
                vn, nn = int(tmp[0]) - 1, int(tmp[2]) - 1
                data.append(vertices[vn])  # + normals[nn]) comment in if you wanna have normals
            else:
                tmp = [part for part in f.split()]
                vn = int(tmp[0]) - 1
                data.append(vertices[vn])

    vb = vbo.VBO(array(data, 'f'))


def main(filename):
    glutInit(sys.argv)

    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(WIDTH, HEIGHT)
    glutCreateWindow("sple openGL/GLUT template")

    glutDisplayFunc(display)  # register display function
    glutReshapeFunc(reshape)  # register reshape function
    glutKeyboardFunc(keyPressed)  # register keyboard function
    glutMouseFunc(mousebuttonpressed)  # register mouse function
    glutMotionFunc(mousemoved)  # register motion function

    # read data
    reset()
    parseObjFile(file(filename))
    initGeometry()

    init(WIDTH, HEIGHT)  # initialize OpenGL state
    glutMainLoop()  # start even processing


if __name__ == "__main__":
    if len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        main(objects['ELEPHANT'])