class Plane(object):
    def __init__(self, point, normal, material):
        self.point = point
        self.normal = normal.normalized()
        self.material = material

    def intersectionParameter(self, ray):
        op = ray.origin - self.point
        a = op.dot(self.normal)
        b = ray.direction.dot(self.normal)

        if b:
            return -a / b
        else:
            return None

    def normalAt(self, p):
        return self.normal

    def __repr__(self):
        return "Plane(p:%s, n:%s)" % (repr(self.point), repr(self.normal))