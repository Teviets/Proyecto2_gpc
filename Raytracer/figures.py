from math import tan, pi, atan2, acos, asin
import fakeNumpy as fnp


class Intercept(object):
    def __init__(self, distance, point, normal, texCoords, obj):
        self.distance = distance
        self.point = point
        self.normal = normal
        self.obj = obj
        self.texCoords = texCoords


class Shape(object):
    def __init__(self, position, material):
        self.position = position
        self.material = material

    def ray_intersect(self, orig, dir):
        return None


class Sphere(Shape):
    def __init__(self, position, radius, material):
        self.radius = radius
        super().__init__(position, material)

    def ray_intersect(self, orig, dir):
        L = fnp.elementwise_subtract(self.position, orig) #subtractVectors(self.position, orig)
        magnitudL = fnp.vectorMagnitude(L)
        L = list(L)
        tca = fnp.dot_product(L, dir)
        d = (magnitudL ** 2 - tca ** 2) ** 0.5

        if type(d) is complex:
            d = float(d.real)

        if d > self.radius:
            return None

        thc = (self.radius ** 2 - d ** 2) ** 0.5
        t0 = tca - thc
        t1 = tca + thc

        if t0 < 0:
            t0 = t1
        if t0 < 0:
            return None

        dir = fnp.ScalarPerVector(dir, t0)
        point = [orig[i] + dir[i] for i in range(3)]
        normal = fnp.elementwise_subtract(point, self.position)
        normal = fnp.normalVector(normal)

        u = (atan2(normal[2], normal[0]) / (2 * pi)) + 0.5
        v = acos(normal[1]) / pi

        return Intercept(t0, point, normal, (u, v), self)


class Plane(Shape):
    def __init__(self, position, normal, material):
        self.normal = fnp.normalVector(normal)
        super().__init__(position=position, material=material)

    def ray_intersect(self, orig, dir):
    
        denom = fnp.dot_product(dir, self.normal)

        if (abs(denom) <= 0.0001):
            return None

        num = fnp.dot_product((fnp.elementwise_subtract(self.position, orig)), self.normal)
        t = num / denom

        if (t < 0):
            return None
        
        
        point = fnp.addVectors(orig, fnp.ScalarPerVector(dir, t))

        return Intercept(t, point, self.normal, None, self)


class Disk(Plane):
    def __init__(self, position, normal, radius, material):
        self.radius = radius
        super().__init__(position=position, normal=normal, material=material)

    def ray_intersect(self, orig, dir):
        planeIntersect = super().ray_intersect(orig, dir)

        if planeIntersect is None:
            return None

        contactDistance = fnp.elementwise_subtract(planeIntersect.point, self.position)

        contactDistance = fnp.vectorMagnitude(contactDistance)

        if (contactDistance > self.radius):
            return None

        return Intercept(planeIntersect.distance, planeIntersect.point, self.normal, None, self)


class AABB(Shape):
    def __init__(self, position, size, material):
        super().__init__(position=position, material=material)

        self.size = size
        self.planes = []

        leftPlane = Plane(position=fnp.NewAddVectors(position, [-size[0] / 2, 0, 0]), normal=(-1, 0, 0), material=material)
        rightPlane = Plane(position=fnp.NewAddVectors(position, [size[0] / 2, 0, 0]), normal=(1, 0, 0), material=material)

        bottomPlane = Plane(position=fnp.NewAddVectors(position, [0, -size[1] / 2, 0]), normal=(0, -1, 0), material=material)
        topPlane = Plane(position=fnp.NewAddVectors(position, [0, size[1] / 2, 0]), normal=(0, 1, 0), material=material)

        frontPlane = Plane(position=fnp.NewAddVectors(position, [0, 0, -size[2] / 2]), normal=(0, 0, -1), material=material)
        backPlane = Plane(position=fnp.NewAddVectors(position, [0, 0, size[2] / 2]), normal=(0, 0, 1), material=material)

        self.planes.append(leftPlane)
        self.planes.append(rightPlane)
        self.planes.append(bottomPlane)
        self.planes.append(topPlane)
        self.planes.append(frontPlane)
        self.planes.append(backPlane)

        self.boundsMin = [0, 0, 0]
        self.boundsMax = [0, 0, 0]

        self.bias = 0.001

        for i in range(3):
            self.boundsMin[i] = self.position[i] - (self.bias + size[i] / 2)
            self.boundsMax[i] = self.position[i] + (self.bias + size[i] / 2)

    def ray_intersect(self, orig, dir):
        intercept = None

        t = float('inf')
        u = v = 0

        for plane in self.planes:
            planeIntersect = plane.ray_intersect(orig=orig, dir=dir)

            if planeIntersect is not None:
                planePoint = planeIntersect.point

                if self.boundsMin[0] < planePoint[0] < self.boundsMax[0]:
                    if self.boundsMin[1] < planePoint[1] < self.boundsMax[1]:
                        if self.boundsMin[2] < planePoint[2] < self.boundsMax[2]:
                            if planeIntersect.distance < t:
                                t = planeIntersect.distance
                                intercept = planeIntersect

                                if abs(plane.normal[0]) > 0:
                                    u = (planePoint[1] - self.boundsMin[1]) / (self.size[1] + self.bias * 2)
                                    v = (planePoint[2] - self.boundsMin[2]) / (self.size[2] + self.bias * 2)
                                elif abs(plane.normal[1]) > 0:
                                    u = (planePoint[0] - self.boundsMin[0]) / (self.size[0] + self.bias * 2)
                                    v = (planePoint[2] - self.boundsMin[2]) / (self.size[2] + self.bias * 2)
                                elif abs(plane.normal[2]) > 0:
                                    u = (planePoint[0] - self.boundsMin[0]) / (self.size[0] + self.bias * 2)
                                    v = (planePoint[1] - self.boundsMin[1]) / (self.size[1] + self.bias * 2)

        if intercept is None:
            return None

        return Intercept(t, intercept.point, intercept.normal, (u, v), self)

class OvalSphere(Shape):
    def __init__(self, position, radius_x, radius_y, material):
        self.radius_x = radius_x
        self.radius_y = radius_y
        super().__init__(position, material)

    def ray_intersect(self, orig, dir):
        # Translate the ray to the local coordinate system of the oval sphere
        local_orig = fnp.elementwise_subtract(orig, self.position)
        dir = list(dir)
        # Ensure that `dir` is a 3D vector
        if len(dir) != 3:
            return None  # Return None if `dir` is not a 3D vector

        # Solve for the intersection using the equation of the oval sphere
        a = (dir[0] ** 2) / (self.radius_x ** 2) + (dir[1] ** 2) / (self.radius_y ** 2) + (dir[2] ** 2)
        b = 2 * (local_orig[0] * dir[0] / (self.radius_x ** 2) + local_orig[1] * dir[1] / (self.radius_y ** 2) + local_orig[2] * dir[2])
        c = (local_orig[0] ** 2) / (self.radius_x ** 2) + (local_orig[1] ** 2) / (self.radius_y ** 2) + (local_orig[2] ** 2) - 1
        
        discriminant = b ** 2 - 4 * a * c
        
        if discriminant < 0:
            # No intersection
            return None
        
        t1 = (-b - discriminant ** 0.5) / (2 * a)
        t2 = (-b + discriminant ** 0.5) / (2 * a)
        
        t = min(t1, t2) if t1 >= 0 else t2
        
        if t >= 0:
            # Calculate the intersection point in world coordinates
            intersection_point = fnp.addVectors(orig, fnp.ScalarPerVector(dir, t))
            
            # Calculate the normal at the intersection point
            normal = fnp.normalVector(fnp.elementwise_subtract(intersection_point, self.position))
            
            # Calculate texture coordinates (you can adjust this to your needs)
            u = (atan2(local_orig[1], local_orig[0]) + pi) / (2 * pi)
            local_orig[2] = min(max(local_orig[2], -1.0), 1.0)
            v = (asin(local_orig[2]) + pi / 2) / pi

            return Intercept(t, intersection_point, normal, (u, v), self)
        
        return None

class Triangle(Shape):
    def __init__(self, material, v0, v1, v2):
        self.v0 = v0
        self.v1 = v1
        self.v2 = v2

        position = [(v0[0] + v1[0] + v2[0]) / 3,
                    (v0[1] + v1[1] + v2[1]) / 3,
                    (v0[2] + v1[2] + v2[2]) / 3]
        super().__init__(position=position, material=material)

    def ray_intersect(self, orig, dir):
        edge0 = fnp.elementwise_subtract(self.v1, self.v0)
        edge1 = fnp.elementwise_subtract(self.v2, self.v1)
        edge2 = fnp.elementwise_subtract(self.v0, self.v2)
        normal = fnp.CrossProduct(edge0, fnp.elementwise_subtract(self.v2, self.v0))
        normal = fnp.normalVector(normal)

        denom = fnp.dot_product(normal, dir)
        if (abs(denom) <= 0.0001):
            return None

        d = -1 * fnp.dot_product(normal, self.v0)

        num = - 1 * (fnp.dot_product(normal, orig) + d)
        t = num / denom

        if t < 0:
            return None

        p = fnp.NewAddVectors(orig, fnp.ScalarPerVector(dir, t))

        vp0 = fnp.elementwise_subtract(p, self.v0)
        vp1 = fnp.elementwise_subtract(p, self.v1)
        vp2 = fnp.elementwise_subtract(p, self.v2)

        c0 = fnp.CrossProduct(edge0, vp0)
        c1 = fnp.CrossProduct(edge1, vp1)
        c2 = fnp.CrossProduct(edge2, vp2)

        if ((fnp.dot_product(normal, c0) < 0) or (fnp.dot_product(normal, c1) < 0) or (fnp.dot_product(normal, c2) < 0)):
            return None

        uv = fnp.barycentricCoords(self.v0, self.v1, self.v2, p)

        return Intercept(t, p, normal, uv, self)


# Torus

class Torus(Shape):
    def __init__(self, position,  external_radius, internal_radius, material):
        self.external_radius = external_radius
        self.internal_radius = internal_radius

        super().__init__(position, material)

    def ray_intersect(self, orig, dir):

        # Ray intersect of torus
        # https://www.geometrictools.com/Documentation/IntersectionTorusRay.pdf

        # Translate the ray to the local coordinate system of the torus
        local_orig = fnp.elementwise_subtract(orig, self.position)

        # Ensure that `dir` is a 3D vector
        if len(dir) != 3:
            return None
        
        # Solve for the intersection using the equation of the torus
        a = fnp.vectorMagnitude(dir)
        b = 2 * fnp.dot_product(local_orig, dir)
        c = fnp.vectorMagnitude(local_orig) + self.external_radius ** 2 - self.internal_radius ** 2

        discriminant = b ** 2 - 4 * a * c

        if discriminant < 0:
            # No intersection
            return None
        
        t1 = (-b - discriminant ** 0.5) / (2 * a)
        t2 = (-b + discriminant ** 0.5) / (2 * a)

        t = min(t1, t2) if t1 >= 0 else t2

        if t >= 0:
            # Calculate the intersection point in world coordinates
            intersection_point = fnp.addVectors(orig, fnp.ScalarPerVector(dir, t))
            
            # Calculate the normal at the intersection point
            normal = fnp.normalVector(fnp.elementwise_subtract(intersection_point, self.position))
            
            # Calculate texture coordinates (you can adjust this to your needs)
            u = (atan2(normal[2], normal[0]) / (2 * pi)) + 0.5
            v = acos(normal[1]) / pi

            return Intercept(t, intersection_point, normal, (u, v), self)
        
        return None
    

# Obj 

def load_obj(filename, material):
    vertices = []
    normals = []
    texcoords = []
    faces = []

    for line in open(filename, "r"):
        if line.startswith('#'): continue
        values = line.split()
        if not values: continue

        if values[0] == 'v':
            vertices.append(list(map(float, values[1:4])))
        elif values[0] == 'vn':
            normals.append(list(map(float, values[1:4])))
        elif values[0] == 'vt':
            texcoords.append(list(map(float, values[1:3])))
        elif values[0] == 'f':
            face_i = []
            texcoords_i = []
            norms_i = []
            for v in values[1:]:
                w = v.split('/')
                face_i.append(int(w[0]))
                texcoords_i.append(int(w[1]))
                norms_i.append(int(w[2]))
            faces.append((face_i, norms_i, texcoords_i))

    model = []
    for face in faces:
        vertices_i = face[0]
        normals_i = face[1]
        texcoords_i = face[2]

        v0 = vertices[vertices_i[0] - 1]
        v1 = vertices[vertices_i[1] - 1]
        v2 = vertices[vertices_i[2] - 1]

        normal = normals[normals_i[0] - 1]

        uv0 = texcoords[texcoords_i[0] - 1]
        uv1 = texcoords[texcoords_i[1] - 1]
        uv2 = texcoords[texcoords_i[2] - 1]

        model.append(Triangle(material, v0, v1, v2))

    return model

