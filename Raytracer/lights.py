import fakeNumpy as fnp


class Light(object):
    def __init__(self, intensity = 1, color = (1, 1, 1), lightType = "None"):
        self.intensity = intensity
        self.color = color
        self.lightType = lightType

    def getLightColor(self):
        return [self.color[0] * self.intensity,
                self.color[1] * self.intensity,
                self.color[2] * self.intensity]

    def getDifusseColor(self, intercept):
        return None

    def getSpecularColor(self, intercept, viewPos):
        return None

class AmbientLight(Light):
    def __init__(self, intensity = 1, color = (1, 1, 1)):
        super().__init__(intensity, color, "Ambient")


class DirectionalLight(Light):
    def __init__(self, direction = (0, -1, 0), intensity = 1, color = (1, 1, 1)):
        self.direction = fnp.normalVector(direction)
        super().__init__(intensity, color, "Directional")

    def getDiffuseColor(self, intercept):

        dir = [(i *-1) for i in self.direction]
        intensity = fnp.dot_product(intercept.normal, dir) * self.intensity
        intensity = max(0, min(1, intensity))

        diffuseColor = [(i * intensity) for i in self.color]

        return diffuseColor

    def getSpecularColor(self, intercept, viewPos):
        dir = fnp.ScalarPerVector(self.direction,-1)

        reflect = fnp.VectorReflected(dir, intercept.normal)

        viewDir = fnp.elementwise_subtract(viewPos, intercept.point)
        viewDir = fnp.normalVector(viewDir)

        specIntensity = max(0, fnp.dot_product(viewDir, reflect)) ** intercept.obj.material.specular
        specIntensity *= intercept.obj.material.ks
        specIntensity *= self.intensity

        specColor = fnp.ScalarPerVector(self.color, specIntensity)

        return specColor


class PointLight(Light):
    def __init__(self, point = (0, 0, 0), intensity = 1, color = (1, 1, 1)):
        self.point = point
        super().__init__(intensity, color, "Point")

    def getDiffuseColor(self, intercept):
        dir = fnp.elementwise_subtract(self.point, intercept.point)
        R = fnp.vectorMagnitude(dir)
        dir = fnp.normalVector(dir)

        intensity = fnp.dot_product(intercept.normal, dir) * self.intensity
        intensity *= 1 - intercept.obj.material.ks

        if R != 0:
            intensity /= R ** 2

        intensity = max(0, min(1, intensity))

        diffuseColor = fnp.ScalarPerVector(self.color, intensity)

        return diffuseColor

    def getSpecularColor(self, intercept, viewPos):
        dir = fnp.elementwise_subtract(self.point, intercept.point)
        R = fnp.vectorMagnitude(dir)
        dir = fnp.normalVector(dir)
        reflect = fnp.VectorReflected(dir, intercept.normal)

        viewDir = fnp.elementwise_subtract(viewPos, intercept.point)
        viewDir = fnp.normalVector(viewDir)

        specIntensity = max(0, fnp.dot_product(viewDir, reflect)) ** intercept.obj.material.specular
        specIntensity *= intercept.obj.material.ks
        specIntensity *= self.intensity

        if R != 0:
            specIntensity /= R ** 2

        specIntensity = max(0, min(1, specIntensity))

        specColor = fnp.ScalarPerVector(self.color, specIntensity)

        return specColor
