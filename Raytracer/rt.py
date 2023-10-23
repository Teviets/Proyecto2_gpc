from math import tan, pi, atan2, acos
from materials import OPAQUE, REFLECTIVE, TRANSPARENT
import fakeNumpy as fnp


maxRecursionDepth = 3


class Raytracer(object):
    def __init__(self, screen):
        self.screen = screen
        _, _, self.width, self.height = screen.get_rect()

        self.scene = []
        self.lights = []

        self.camPosition = [0, 0, 0]

        self.rtViewPort(0, 0, self.width, self.height)
        self.rtProjection()

        self.rtClearColor(0, 0, 0)
        self.rtColor(1, 1, 1)
        self.rtClear()

        self.model = None

        self.envMap = None

    def rtClearColor(self, r, g, b):
        self.clearColor = (r * 255, g * 255, b * 255)

    def rtClear(self):
        self.screen.fill(self.clearColor)

    def rtColor(self, r, g, b):
        self.currColor = (r * 255, g * 255, b * 255)

    def rtPoint(self, x, y, color=None):
        y = self.height - y
        if (0 <= x <= self.width) and (0 <= y <= self.height):
            if color != None:
                color = (int(color[0] * 255),
                         int(color[1] * 255),
                         int(color[2] * 255))
                self.screen.set_at((x, y), color)
            else:
                self.screen.set_at((x, y), self.currColor)

    def rtCastRay(self, orig, dir, sceneObj=None, recursion=0):
        if recursion >= maxRecursionDepth:
            return None

        intersect = None
        hit = None
        depth = float('inf')
        for obj in self.scene:
            if sceneObj != obj:
                
                intersect = obj.ray_intersect(orig, dir)

                if intersect != None:
                    if intersect.distance < depth:
                        hit = intersect
                        depth = intersect.distance

        return hit

    def rtRayColor(self, intercept, rayDirection, recursion=0):
        if intercept is None:
            if self.envMap:
                x = (atan2(rayDirection[2], rayDirection[0]) / (2 * pi) + 0.5) * self.envMap.get_width()
                y = acos(rayDirection[1]) / pi * self.envMap.get_height()

                envColor = self.envMap.get_at((int(x), int(y)))

                return [i / 255 for i in envColor]
            else:
                return None

        material = intercept.obj.material

        finalColor = [0, 0, 0]
        surfaceColor = material.diffuse

        if material.texture and intercept.texCoords:
            tx = max(0, min(int(intercept.texCoords[0] * material.texture.get_width() - 1), material.texture.get_width() - 1))
            ty = max(0, min(int(intercept.texCoords[1] * material.texture.get_height() - 1), material.texture.get_height() - 1))


            texColor = material.texture.get_at((int(tx), int(ty)))
            texColor = [i / 255 for i in texColor]
            surfaceColor = [surfaceColor[i] * texColor[i] for i in range(3)]

        ambientColor = [0, 0, 0]
        diffuseColor = [0, 0, 0]
        specularColor = [0, 0, 0]
        reflectColor = [0, 0, 0]
        refractColor = [0, 0, 0]

        if material.matType == OPAQUE:
            for light in self.lights:
                if light.lightType == "Ambient":
                    ambientColor = [(ambientColor[i]+light.getLightColor()[i]) for i in range(3)]
                else:
                    lightDir = None
                    if light.lightType == "Directional":
                        lightDir = [(i*-1) for i in light.direction]
                    elif light.lightType == "Point":
                        lightDir = fnp.elementwise_subtract(light.point, intercept.point)
                        lightDistance = fnp.normalize(lightDir)
                        lightDir = fnp.divTF(lightDir, lightDistance)
                        
                    shadowIntersect = self.rtCastRay(intercept.point, lightDir, intercept.obj)

                    if shadowIntersect==None or (light.lightType=="Point" and shadowIntersect != None and shadowIntersect.distance > lightDistance):
                        diffuseColor = [(diffuseColor[i]+light.getDiffuseColor(intercept)[i]) for i in range(3)]
                        specularColor = [(specularColor[i]+light.getSpecularColor(intercept, self.camPosition)[i]) for i in range(3)]

        elif material.matType == REFLECTIVE:
            reflect = fnp.VectorReflected(intercept.normal, fnp.ScalarPerVector(rayDirection,-1))
            reflectIntercept = self.rtCastRay(orig=intercept.point, dir=reflect, sceneObj=intercept.obj, recursion=recursion + 1)
            reflectColor = self.rtRayColor(intercept=reflectIntercept, rayDirection=reflect, recursion=recursion + 1)
            
            for light in self.lights:
                if light.lightType != "Ambient":
                    lightDir = None
                    if light.lightType == "Directional":
                        lightDir = [(i*-1) for i in light.direction]
                    elif light.lightType == "Point":
                        lightDir = fnp.elementwise_subtract(light.point, intercept.point)
                        lightDistance = fnp.normalize(lightDir)
                        lightDir = fnp.divTF(lightDir, fnp.normalVector(lightDir))
                        
                    shadowIntersect = self.rtCastRay(orig=intercept.point, dir=lightDir, sceneObj=intercept.obj)
                    
                    if shadowIntersect==None or (light.lightType=="Point" and shadowIntersect != None and shadowIntersect.distance > lightDistance):
                        specularColor = [(specularColor[i]+light.getSpecularColor(intercept, self.camPosition)[i]) for i in range(3)]

        elif material.matType == TRANSPARENT:
            isOutside = fnp.dot_product(rayDirection, intercept.normal) < 0
            factor = 0.001
            bias = [elemento * factor for elemento in intercept.normal]
            
            factor = -1
            negativeRayDirection = [elemento * factor for elemento in rayDirection]
            reflectRay = fnp.VectorReflected(intercept.normal, negativeRayDirection)
            reflectOrigin = fnp.NewAddVectors(intercept.point, bias) if isOutside else fnp.elementwise_subtract(intercept.point, bias)
            reflectIntercept = self.rtCastRay(reflectOrigin, reflectRay, None, recursion + 1)
            reflectColor = self.rtRayColor(reflectIntercept, reflectRay, recursion + 1)

            for light in self.lights:
                if light.lightType != "Ambient":
                    shadowDirection = None
                    if light.lightType == "Directional":
                        shadowDirection = [i * -1 for i in light.direction]
                    if light.lightType == "Point":
                        lightDirection = fnp.elementwise_subtract(light.point, intercept.point)
                        lightDistance = fnp.normalize(lightDirection)
                        shadowDirection = fnp.divTF(lightDirection, fnp.normalize(lightDirection))
                        
                    shadowIntersect = self.rtCastRay(intercept.point, shadowDirection, intercept.obj)

                    if shadowIntersect is None or (light.lightType=="Point" and shadowIntersect != None and shadowIntersect.distance > lightDistance):
                        specColor = light.getSpecularColor(intercept, self.camPosition)
                        specularColor = [specularColor[i] + specColor[i] for i in range(3)]

            if not fnp.InternalReflection(intercept.normal, rayDirection, 1.0, intercept.obj.material.ior):
                refractRay = fnp.refractVector(intercept.normal, rayDirection, 1.0, intercept.obj.material.ior)
                refractOrigin = fnp.elementwise_subtract(intercept.point, bias) if isOutside else fnp.NewAddVectors(intercept.point, bias)
                refractIntercept = self.rtCastRay(refractOrigin, refractRay, None, recursion + 1)
                refractColor = self.rtRayColor(refractIntercept, refractRay, recursion + 1)

                kr, kt = fnp.fresnel(intercept.normal, rayDirection, 1.0, intercept.obj.material.ior)
                reflectColor = fnp.ScalarPerVector(reflectColor,kr)
                refractColor = fnp.ScalarPerVector(refractColor,kt) 

        lightColor = [(ambientColor[i] + diffuseColor[i] + specularColor[i] + reflectColor[i] + refractColor[i]) for i in range(3)]
        finalColor = [min(1, (surfaceColor[i] * lightColor[i])) for i in range(3)]

        return finalColor

    def rtRender(self):
        for x in range(self.vpX, self.vpX + self.vpWidth + 1):
            for y in range(self.vpY, self.vpY + self.vpHeight + 1):
                if (0 <= x <= self.width) and (0 <= y <= self.height):
                    px = ((x + 0.5 - self.vpX) / self.vpWidth) * 2 - 1
                    py = ((y + 0.5 - self.vpY) / self.vpHeight) * 2 - 1

                    px *= self.rightEdge
                    py *= self.topEdge

                    direction = (px, py, -self.nearPlane)
                    direction = fnp.normalVector(direction)

                    intercept = self.rtCastRay(self.camPosition, direction)

                    rayColor = self.rtRayColor(intercept, direction)

                    if rayColor:
                        self.rtPoint(x, y, rayColor)

    def rtViewPort(self, posX, posY, width, height):
        self.vpX = posX
        self.vpY = posY
        self.vpWidth = width
        self.vpHeight = height

    def rtProjection(self, fov=60, n=0.1):
        aspectRatio = self.vpWidth / self.vpHeight
        self.nearPlane = n
        self.topEdge = tan((fov * pi / 180) / 2) * self.nearPlane
        self.rightEdge = self.topEdge * aspectRatio

