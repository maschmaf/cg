from Color import Color
from Vector import Vector

class Material(object):
    def __init__(self, color, ambientComp = 0.8, diffusComp = 0.8, specularComp = 0.2, gloss=0.1):
        self.color = color
        self.ambientComp = ambientComp
        self.diffusComp = diffusComp
        self.specularComp = specularComp
        self.gloss = gloss

    def calculateAmbientColor(self, objectColor, environmentColor, point = None):

        if isinstance(objectColor, CheckerBoardMaterial):
            objectColor = objectColor.baseColorAt(point)

        ambient_vector = objectColor.scale(self.ambientComp) # berechnung object_color * ambientComp(skalare groesse)

        # berechnung vektor mal vektor (nur bei Farbe)
        x = environmentColor.getVec()[0] * ambient_vector.getVec()[0]
        y = environmentColor.getVec()[1] * ambient_vector.getVec()[1]
        z = environmentColor.getVec()[2] * ambient_vector.getVec()[2]
        colorVector = ([x, y, z])
        return Color(colorVector)

    def calculateDiffusColor(self, objectColor, lightColor, raylight_direction, hitPointNormale):
        diff_vector = objectColor.scale(self.diffusComp) # berechnung object_color * diffusComp(skalare groesse)

        scalar = raylight_direction.dot(hitPointNormale) # scalarprodukt von lichtstrahl und normale des getroffenen punktes

        if scalar >= 0:
            # berechnung vektor mal vektor (nur bei Farbe)
            x = lightColor.getVec()[0] * diff_vector.getVec()[0]
            y = lightColor.getVec()[1] * diff_vector.getVec()[1]
            z = lightColor.getVec()[2] * diff_vector.getVec()[2]
            colorVector = Vector([x, y, z])
            colorVector = colorVector.scale(scalar)
            return Color([colorVector.getVec()[0], colorVector.getVec()[1], colorVector.getVec()[2]])
        else:
            return Color([0, 0, 0])

    def calculateSpecularColor(self, objectColor, lightColor, ray_direction, raylight_direction, hitPointNormale, specularN=3):
        specular_vector = objectColor.scale(self.specularComp) # berechnung object_color * specularComp(skalare groesse)

        lightray = (raylight_direction - hitPointNormale.scale((raylight_direction.dot(hitPointNormale))).scale(2)) * (-1)
        scalar = lightray.dot(ray_direction.scale(-1))
        if scalar >= 0:
            # berechnung vektor mal vektor (nur bei Farbe)
            x = lightColor.getVec()[0] * specular_vector.getVec()[0]
            y = lightColor.getVec()[1] * specular_vector.getVec()[1]
            z = lightColor.getVec()[2] * specular_vector.getVec()[2]

            colorVector = Vector([x, y, z])
            colorVector = colorVector.scale(scalar ** specularN)
            return Color([colorVector.getVec()[0], colorVector.getVec()[1], colorVector.getVec()[0]])
        else:
            return Color([0, 0, 0])

    def calculateColor(self, lightColor, environmentColor, objectColor, raylight_direction, ray_direction, hitPointNormale, point = None):

        if isinstance(objectColor, CheckerBoardMaterial):
            objectColor = objectColor.baseColorAt(point)

        ambientColor = self.calculateAmbientColor(objectColor, environmentColor)
        diffColor = self.calculateDiffusColor(objectColor, lightColor, raylight_direction,hitPointNormale)
        specularColor = self.calculateSpecularColor(objectColor, lightColor, ray_direction, raylight_direction, hitPointNormale)

        result_color_vector = ambientColor + specularColor + diffColor
        return Color([result_color_vector.getVec()[0], result_color_vector.getVec()[1], result_color_vector.getVec()[2]])

class CheckerBoardMaterial(object):
    def __init__(self):
        self.baseColor = Color([1,1,1])
        self.otherColor = Color([0,0,0])
        self.ambientComp = 0.8
        self.diffusComp = 0.8
        self.specularComp = 0.2
        self.checkSize = 1

    def baseColorAt(self, p):
        colorVector = Vector([p.getPoint()[0], p.getPoint()[1], p.getPoint()[2]])
        colorVector = colorVector.scale((1.0 / self.checkSize))
        if (int(abs(colorVector.getVec()[0]) + 0.5) + int(abs(colorVector.getVec()[1]) + 0.5) + int(abs(colorVector.getVec()[2]) + 0.5)) % 2:
            return self.otherColor
        return self.baseColor