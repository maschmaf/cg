from Tkinter import *
from Canvas import *
import sys
import numpy as np

WIDTH = 400  # width of canvas
HEIGHT = 400  # height of canvas

HPSIZE = 2  # half of point size (must be integer)
CCOLOR = "#0000FF"  # blue (color of control-points and polygon)

BCOLOR = "#000000"  # black (color of bezier curve)
BWIDTH = 2  # width of bezier curve

controlpoints = []  # list of (control-)points
deboorpoints = []  # list of (control-)points
elementList = []  # list of elements (used by Canvas.delete(...))

k = 4  # Ordnung
max_points = 4  # Max points


def drawPoints(points, color):
    for p in points:
        element = can.create_oval(p[0] - HPSIZE, p[1] - HPSIZE,
                                  p[0] + HPSIZE, p[1] + HPSIZE,
                                  fill=color, outline=color)
        elementList.append(element)


def drawPolygon(points, color):
    if len(points) > 1:
        for i in range(len(points) - 1):
            element = can.create_line(points[i][0], points[i][1],
                                      points[i + 1][0], points[i + 1][1],
                                      fill=color)
            elementList.append(element)


def calc_r(knotvector, t):
    temp_v_idx = 0
    for idx in range(0, len(knotvector) - 1):
        if knotvector[idx] <= t:
            temp_v_idx = idx
    return temp_v_idx


def deboor(k, points, knotvector, t, j):
    r = calc_r(knotvector, t)
    i = r - k + (1 + j)
    if len(points) == 1:
        return points[0]
    newPoints = []

    if j == 1:
        while i <= r:
            alpha = ((t - knotvector[i]) * 1.0) / ((knotvector[i - j + k]) - knotvector[i]) * 1.0

            x = points[i - 1][0]
            y = points[i - 1][1]

            if i < len(controlpoints):
                next_x = points[i][0]
                next_y = points[i][1]
            else:
                next_x = points[i - 1][0]
                next_y = points[i - 1][1]

            bx = (1 - alpha) * x + alpha * next_x
            by = (1 - alpha) * y + alpha * next_y
            b = [bx, by]

            newPoints.append(b)
            i += 1
    else:
        for idx in range(0, len(points) - 1):
            alpha = ((t - knotvector[i]) * 1.0) / ((knotvector[i - j + k]) - knotvector[i]) * 1.0

            x = points[idx][0]
            y = points[idx][1]

            next_x = points[idx + 1][0]
            next_y = points[idx + 1][1]

            bx = (1 - alpha) * x + alpha * next_x
            by = (1 - alpha) * y + alpha * next_y
            b = [bx, by]

            newPoints.append(b)
            i += 1

    return deboor(k, newPoints, knotvector, t, j + 1)


def quit(root=None):
    """ quit programm """
    if root == None:
        sys.exit(0)
    root._root().quit()
    root._root().destroy()


def draw():
    global deboorpoints
    """ draw elements """
    can.delete(*elementList)
    deboorpoints = []
    n = len(controlpoints)
    knotvector = []
    knotvector.extend([0 for x in range(k)])
    last_entry = len(controlpoints) - (k - 2)
    knotvector.extend([x for x in range(1, last_entry)])
    knotvector.extend([last_entry for x in range(k)])

    if k == 1:
        drawPoints(controlpoints, BCOLOR)
    else:
        drawPoints(controlpoints, CCOLOR)
        drawPolygon(controlpoints, CCOLOR)
        if n >= k:
            j = 1
            for t in range(0, max(knotvector) * 10):
                point = deboor(k, controlpoints, knotvector, t / 10.0, j)
                deboorpoints.append(point)
                drawPoints(deboorpoints, BCOLOR)

def clearAll():
    """ clear all (point list and canvas) """
    can.delete(*elementList)
    del controlpoints[:]


def mouseEvent(event):
    """ process mouse events """
    global controlpoints
    if len(controlpoints) < max_points:
        controlpoints.append([event.x, event.y])
    draw()


def grad_update(new):
    global k
    k = int(new)
    draw()


def max_update(new):
    global max_points
    max_points = int(new)
    draw()


if __name__ == "__main__":
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
    k_slider_label = Label(mw, text="Ordnung")
    k_slider = Scale(mw, from_=1, to=10, orient=HORIZONTAL, command=grad_update)
    max_slider_label = Label(mw, text="Anz. Punkte")
    max_slider = Scale(mw, from_=4, to=100, orient=HORIZONTAL, command=max_update)

    k_slider_label.pack()
    k_slider.pack()
    max_slider_label.pack()
    max_slider.pack();

    # start
    mw.mainloop()
