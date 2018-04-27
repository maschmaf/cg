from Camera import Camera
from Color import Color
from Light import Light
from Material import Material, CheckerBoardMaterial
from Plane import Plane
from Point import Point
from Vector import Vector
from Spehre import Spehre
from Triangle import Triangle
from PIL import Image

WIDTH = 400
HEIGHT = 400

def main():
    e = Point([0, 1.8, 10])
    c = Point([0, 3, 0])
    up = Vector([0, 1, 0])
    fov = 45

    aspectRatio = WIDTH / HEIGHT
    image = Image.new('RGB', (WIDTH, HEIGHT))
    backgroundColor = Color([0,0,0])
    environmentColor = Color([0.25,0.25,0.25])

    light = Light(Point([30,30,10]), Color([1,1,1]))

    red = Color([1, 0, 0])
    green = Color([0, 1, 0])
    blue = Color([0, 0 ,1])
    yellow = Color([1,1,0])
    checkerBoard = CheckerBoardMaterial()

    sphere_red = Spehre(Point([2.5, 3, -10]), 2, Material(red))
    sphere_green = Spehre(Point([0, 7, -10]), 2, Material(blue))
    sphere_blue = Spehre(Point([-2.5, 3, -10]), 2, Material(green))

    triangle = Triangle(Point([2.5,3,-10]),Point([-2.5,3,-10]),Point([0,7,-10]), Material(yellow))
    plane = Plane(Point([0,0,0]), Vector([0,1,0]), Material(checkerBoard))

    objectList = [sphere_red, sphere_green, sphere_blue, triangle, plane]

    camera = Camera(e, c, up, WIDTH, HEIGHT, aspectRatio, backgroundColor, objectList, image, light, fov, environmentColor)
    image = camera.raytrace()
    image.show()
    #image.save('Raytrace.png', 'png')

if __name__ =='__main__':
    main()