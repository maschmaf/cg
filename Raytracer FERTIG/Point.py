from Vector import Vector


class Point(object):
    point = [0, 0, 0]
    vec = [0, 0, 0]

    def __init__(self, point):
        self.point = point

    #Punkt + Punkt = Vector
    def __sub__(self, other):
        x = self.point[0] - other.getPoint()[0]
        y = self.point[1] - other.getPoint()[1]
        z = self.point[2] - other.getPoint()[2]
        return Vector([x,y,z])

    #Punkt + Vector = Punkt
    def __add__(self, vector):
        x = self.point[0] + vector.getVec()[0]
        y = self.point[1] + vector.getVec()[1]
        z = self.point[2] + vector.getVec()[2]
        return Point([x, y, z])

    def getPoint(self):
        return Point(self.point)

    def __getitem__(self, item):
        return self.point[item]

    def __repr__(self):
        return "Point(x:%s, y=%s, z=%s)" % (self.point[0], self.point[1], self.point[2])