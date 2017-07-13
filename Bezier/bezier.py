from Tkinter import *
from Canvas import *
import sys

WIDTH = 400  # width of canvas
HEIGHT = 400  # height of canvas

HPSIZE = 2  # half of point size (must be integer)
CCOLOR = "#0000FF"  # blue (color of control-points and polygon)

BCOLOR = "#000000"  # black (color of bezier curve)
BWIDTH = 2  # width of bezier curve

pointList = []  # list of (control-)points
elementList = []  # list of elements (used by Canvas.delete(...))
curveList = []  # list of curve-points


def drawPoints():
    """ draw (control-)points """
    for p in pointList:
        element = can.create_oval(p[0] - HPSIZE, p[1] - HPSIZE,
                                  p[0] + HPSIZE, p[1] + HPSIZE,
                                  fill=CCOLOR, outline=CCOLOR)
        elementList.append(element)


def drawPolygon():
    """ draw (control-)polygon conecting (control-)points """
    if len(pointList) > 1:
        for i in range(len(pointList) - 1):
            element = can.create_line(pointList[i][0], pointList[i][1],
                                      pointList[i + 1][0], pointList[i + 1][1],
                                      fill=CCOLOR)
            elementList.append(element)


def drawPointsBezier(pointList):
    """ draw (control-)points """
    for p in pointList:
        element = can.create_oval(p[0] - HPSIZE, p[1] - HPSIZE,
                                  p[0] + HPSIZE, p[1] + HPSIZE,
                                  fill=BCOLOR, outline=BCOLOR)
        elementList.append(element)


def drawPolygonBezier(pointList):
    """ draw (control-)polygon conecting (control-)points """
    if len(pointList) > 1:
        for i in range(len(pointList) - 1):
            element = can.create_line(pointList[i][0], pointList[i][1],
                                      pointList[i + 1][0], pointList[i + 1][1],
                                      fill=BCOLOR)
            elementList.append(element)


def drawBezierCurve():
    """ draw bezier curve defined by (control-)points """
    curveList = []
    curveList.append(pointList[0])
    # Anzahl der Unterteilungen
    N = 100
    for i in range(1, N + 1):
        t = float(i) / float(N + 1)
        p = casteljau(pointList, t)
        curveList.append(p)
    curveList.append(pointList[-1])
    drawPointsBezier(curveList)
    drawPolygonBezier(curveList)


def casteljau(points, t):
    numPoints = len(points)
    if (numPoints == 1):
        return points[0]
    newPoints = []

    pairs = zip(points[:-1], points[1:])

    for (p, n) in pairs:
        px = p[0] + t * (n[0] - p[0])
        py = p[1] + t * (n[1] - p[1])
        newPoints.append([px, py])

    return casteljau(newPoints, t)


def quit(root=None):
    """ quit programm """
    if root == None:
        sys.exit(0)
    root._root().quit()
    root._root().destroy()


def draw():
    """ draw elements """
    can.delete(*elementList)
    drawPoints()
    drawPolygon()
    drawBezierCurve()


def clearAll():
    """ clear all (point list and canvas) """
    can.delete(*elementList)
    del pointList[:]
    del curveList[:]


def mouseEvent(event):
    """ process mouse events """
    # print "left mouse button clicked at ", event.x, event.y
    pointList.append([event.x, event.y])
    draw()


if __name__ == "__main__":
    # check parameters
    if len(sys.argv) != 1:
        print
        "pointViewerTemplate.py"
        sys.exit(-1)

    # create main window
    mw = Tk()

    # create and position canvas and buttons
    cFr = Frame(mw, width=WIDTH, height=HEIGHT, relief="sunken", bd=1)
    cFr.pack(side="top")
    can = Canvas(cFr, width=WIDTH, height=HEIGHT)
    can.bind("<Button-1>", mouseEvent)
    can.pack()
    cFr = Frame(mw)
    cFr.pack(side="left")
    bClear = Button(cFr, text="Clear", command=clearAll)
    bClear.pack(side="left")
    eFr = Frame(mw)
    eFr.pack(side="right")
    bExit = Button(eFr, text="Quit", command=(lambda root=mw: quit(root)))
    bExit.pack()

    # start
    mw.mainloop()