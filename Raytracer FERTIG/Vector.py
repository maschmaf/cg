import math


class Vector(object):
    v = [0, 0, 0]

    def __init__(self, vector):
        self.v = vector

    def __add__(self, other):
        return Vector([self.v[0] + other.getVec()[0], self.v[1] + other.getVec()[1], self.v[2] + other.getVec()[2]])

    def __sub__(self, other):
        return Vector([self.v[0] - other.getVec()[0], self.v[1] - other.getVec()[1], self.v[2] - other.getVec()[2]])

    def __mul__(self, cons):
        return Vector([self.v[0] * cons, self.v[1] * cons, self.v[2] * cons])

    def reflect(self, other):
        return self - (other.getVec() * 2) * (self.dot(other.getVec()))

    def cross(self, other):
        x = (self.v[1] * other.getVec()[2]) - (self.v[2] * other.getVec()[1])
        y = (self.v[2] * other.getVec()[0]) - (self.v[0] * other.getVec()[2])
        z = (self.v[0] * other.getVec()[1]) - (self.v[1] * other.getVec()[0])
        return Vector([x,y,z])

    def div(self, const):
        x = self.v[0] / const
        y = self.v[1] / const
        z = self.v[2] / const
        return Vector([x, y, z])

    def scale(self, const):
        return Vector([self.v[0] * const, self.v[1] * const, self.v[2] * const])

    def normalized(self):
        length = self.norm()
        return Vector([self.v[0] / length, self.v[1] / length, self.v[2] / length])

    def norm(self):
        return math.sqrt((self.v[0] * self.v[0]) + (self.v[1] * self.v[1]) + (self.v[2] * self.v[2]))

    def dot(self, other):
        return float(self.v[0] * other.getVec()[0] + self.v[1] * other.getVec()[1] + self.v[2] * other.getVec()[2])

    def getVec(self):
        return Vector(self.v)

    def __getitem__(self, item):
        return self.v[item]

    def __repr__(self):
        return "Vector(x:%s, y:%s, z:%s)" % (self.v[0], self.v[1], self.v[2])