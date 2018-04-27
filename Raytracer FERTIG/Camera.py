from Color import Color
from Plane import Plane
from Triangle import Triangle
from Vector import Vector
from Spehre import Spehre
from Point import Point
import math
from Ray import Ray

class Camera(object):
    #Kameraparameter
    e = Point([0, 0, 0])
    c = Point([0, 0, 0])
    up = Vector([0, 0, 0])
    f = Vector([0, 0, 0])
    s = Vector([0, 0, 0])
    u = Vector([0, 0, 0])

    def __init__(self, e, c, up, wRes, hRes, aspectRatio, backgroundColor, objectList, image, light, fov, environmentColor, maxrecursion=2):
        self.e = e
        self.c = c
        self.up = up
        self.f = (c - e).normalized()
        self.s = (self.f.cross(self.up)).normalized()
        self.u = (self.s.cross(self.f)).scale(-1)

        self.wRes = wRes
        self.hRes = hRes

        self.backgroundColor = backgroundColor
        self.image = image

        self.objectList = objectList

        self.fov = fov
        self.alpha = self.fov / 2.0
        self.height = 2 * math.tan(self.alpha)
        self.width = aspectRatio * self.height

        self.pixelWidth = self.width / (self.wRes - 1)
        self.pixelHeight = self.height / (self.hRes - 1)

        self.light = light
        self.environmentColor = environmentColor
        self.lightColor = self.light.color

        self.maxrecursion = maxrecursion

    # Der Ray Casting Algorithmus
    def raytrace(self, recursionlevel = 1,):
        for x in range(self.wRes):
            for y in range(self.hRes):
                ray = self.calculateRay(x, y)
                colorAsVector = self.renderRay(recursionlevel, ray)
                colorAsRGB = colorAsVector.setColorToRGB(colorAsVector)
                self.image.putpixel((x, y), colorAsRGB)
        return self.image

    # berechnet, ob der Breich im Schatten liegt oder nicht
    def isInShadow(self, raylight):
        for obj in self.objectList:
            hit = obj.intersectionParameter(raylight)
            if hit and hit > 0.001:
                return True
        return False

    # gibt das naehste Objekt zurueck
    def getClosestObject(self, ray):
        closestDistance = float("inf")
        closestObject = None
        for obj in self.objectList:
            hitDistance = obj.intersectionParameter(ray)
            if hitDistance:
                if hitDistance > 0 and hitDistance < closestDistance:
                    closestDistance = hitDistance
                    closestObject = obj
        return (closestDistance, closestObject)

    # Rekursiv die Farbe / die Reflexion rendern
    def renderRay(self, level, ray):
        (closestDistance, closestObject) = self.getClosestObject(ray)
        if closestDistance > 0.001 and closestDistance < float("inf"):
            hitPoint = ray.origin + ray.direction.scale(closestDistance)
            hitPointNormale = closestObject.normalAt(hitPoint)
            raylight = self.createRayLight(ray.pointAtParameter(closestDistance))
            color = closestObject.material.color
            #Schattenberechnung
            if self.isInShadow(raylight):
                #Punkt liegt im Schatten
                color = closestObject.material.calculateAmbientColor(closestObject.material.color, self.environmentColor, hitPoint)
            else:
                # Punkt liegt nicht im Schatten
                color = closestObject.material.calculateColor(self.lightColor, self.environmentColor, closestObject.material.color,
                                                    raylight.direction, ray.direction, hitPointNormale, hitPoint)

            #Ist das Objekt vom Type Plane(Ebene) wird keine reflexion Berechnet...
            if level >= self.maxrecursion or isinstance(closestObject, Plane):
                return color

            #... ansonsten schon
            reflectionRay = Ray(hitPoint, ray.direction.reflect(hitPointNormale))
            reflectionColor = self.renderRay(level+1, reflectionRay)

            red = color.getVec()[0] + (reflectionColor.getVec()[0] * closestObject.material.gloss)
            green = color.getVec()[1] + (reflectionColor.getVec()[1] * closestObject.material.gloss)
            blue = color.getVec()[2] + (reflectionColor.getVec()[2] * closestObject.material.gloss)
            return Color([red,green,blue])

        else:
            return self.backgroundColor

    # berechnung des Strahls von der Camera zum ObjektPunkt
    def calculateRay(self,x,y):
        xComp = self.s.scale(x * self.pixelWidth - self.width / 2)
        yComp = self.u.scale(y * self.pixelHeight - self.height / 2)
        ray = Ray(self.e, self.f + xComp + yComp)
        return ray

    # Berechnung des Strahls von einem Punkt zur Lichtquelle
    def createRayLight(self, origin):
        ray = Ray(origin, (self.light.point - origin))
        return ray

    def __repr__(self):
        return "Camera(e:%s, c:%s, up:%s, f:%s, s:%s, u:%s)" % (repr(self.e), repr(self.c), repr(self.up), repr(self.f), repr(self.s), repr(self.u))