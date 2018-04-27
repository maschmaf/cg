from Vector import Vector


class Color(Vector):

    maxRGB = 255
    colorV = Vector([0,0,0])
    def __init__(self, colorV):
        self.colorV = Vector.__init__(self, colorV)

    def setColorToRGB(self, vec):
        return (int(vec.getVec()[0] * self.maxRGB), int(vec.getVec()[1] * self.maxRGB), int(vec.getVec()[2] * self.maxRGB))