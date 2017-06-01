#!/usr/bin/python3
# -*- coding: utf-8 -*-
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.arrays import vbo
from numpy import array

import sys, math
p1 = [-1.0, 0.1]
p2 = [-0.9, 0.2]
p3 = [-0.8, 0.1]
p4 = [-0.7, 0.2]
p5 = [-0.6, 0.1]
p6 = [-0.5, 0.2]
p7 = [-0.4, 0.1]
p8 = [-0.3, 0.2]
p9 = [-0.4, 0.3]
p10 = [-0.2, 0.3]
p11 = [-0.1, 0.2]
p12 = [-0.0, 0.3]
p13 = [0.1, 0.2]
p14 = [0.2, 0.3]

rect1 = [p1, p2, p3]
rect2 = [p2, p3, p4]
rect3 = [p3, p4, p5]
rect4 = [p4, p5, p6]
rect5 = [p5, p6, p7]
rect6 = [p6, p7, p8]
rect7 = [p6, p8, p9]
rect8 = [p8, p9, p10]
rect9 = [p8, p10, p11]
rect10 = [p10, p11, p12]
rect11 = [p11, p12, p13]
rect12 = [p12, p13, p14]
points = [rect1, rect2, rect3, rect4, rect5, rect6, rect7, rect8, rect9, rect10, rect11, rect12]
vbo = vbo.VBO(array(points, 'f'))

WIDTH = 500
HEIGTH = 500

def initGL(width, heigth):
    glClearColor(0.0, 0.0, 1.0, 0.0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-1.5, 1.5, -1.5, 1.5, -1.0, 1.0)
    glMatrixMode(GL_MODELVIEW)

def display():
    glClear(GL_COLOR_BUFFER_BIT)
    glColor3f(.75,.75,.75)
    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

    vbo.bind()
    glVertexPointerf(vbo)
    glEnableClientState(GL_VERTEX_ARRAY)
    glDrawArrays(GL_TRIANGLE_STRIP, 0, 36)
    vbo.unbind()
    glDisableClientState(GL_VERTEX_ARRAY)

    glFlush()

def main(args):
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
    glutInitWindowSize(WIDTH, HEIGTH)
    glutCreateWindow("GL_TRIANGLES")
    glutDisplayFunc(display)
    initGL(500, 500)
    glutMainLoop()

if __name__ == '__main__':
    main(sys.argv[1:])
