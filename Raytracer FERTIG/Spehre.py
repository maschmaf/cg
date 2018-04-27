import math


class Spehre(object):
    def __init__(self, c, r, material):
        self.center = c #Point
        self.radius = r
        self.material = material

    def __repr__(self):
        return "Sphere(c:%s, r:%s)" % (repr(self.center), repr(self.radius))

    def intersectionParameter(self, ray):
         co = self.center - ray.origin
         v = co.dot(ray.direction)
         discriminant = (self.radius * self.radius) - (co.dot(co) - v * v)
         if discriminant < 0:
             return None
         else:
             return v - math.sqrt(discriminant)

    def normalAt(self, p):
        return (p - self.center).normalized()