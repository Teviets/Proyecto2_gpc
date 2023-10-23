import math

def timeMatrix (matrix1, matrix2):
    #multiply two matrices
    
    result = []
    for i in range(len(matrix1)):
        result.append([])
        for j in range(len(matrix2[0])):
            result[i].append(0)
            for k in range(len(matrix2)):
                result[i][j] += matrix1[i][k] * matrix2[k][j]

    return result
        
    
def timeMatrixSingle(matrix1, matrix2):
    filas_matriz = len(matrix1)
    columnas_matriz = len(matrix1[0])
    longitud_vector = len(matrix2)

    if columnas_matriz != longitud_vector:
        raise ValueError("El número de columnas de la matriz debe ser igual a la longitud del vector para calcular el producto punto.")

    resultado = [0] * filas_matriz

    for i in range(filas_matriz):
        for j in range(columnas_matriz):
            resultado[i] += matrix1[i][j] * matrix2[j]

    return resultado

def elementwise_multiply(vector1, vector2):
    if len(vector1) != len(vector2):
        raise ValueError("Los vectores deben tener la misma longitud para la multiplicación elemento por elemento.")
    
    result = [v1 * v2 for v1, v2 in zip(vector1, vector2)]
    return result

def elementwise_subtract(vector1, vector2):
    if len(vector1) != len(vector2):
        raise ValueError("Los vectores deben tener la misma longitud para la resta elemento por elemento.")
    
    result = [v1 - v2 for v1, v2 in zip(vector1, vector2)]
    return result

def vector_addition(vector1, scalar, vector2):
    if len(vector1) != len(vector2):
        raise ValueError("Los vectores deben tener la misma longitud para la suma.")
    
    result = [v1 + scalar * v2 for v1, v2 in zip(vector1, vector2)]
    return result

def addVectors(v1, v2):
    if len(v1) != len(v2):
        raise ValueError("Error")

    resultado = [v1[i] + v2[i] for i in range(len(v1))]
    return resultado



# fun matrix times vector
def timeMatrixVector(matrix, vector):
    result = []
    for i in range(len(matrix)):
        result.append([])
        for j in range(len(vector[0])):
            result[i].append(0)
            for k in range(len(vector)):
                result[i][j] += matrix[i][k] * vector[k][j]

    return result

# fun barycentric coords with cross product
def barycentricCoords(A, B, C, P):
    areaPCB = (B[1] - C[1]) * (P[0] - C[0]) + (C[0] - B[0]) * (P[1] - C[1])
    areaABC = (B[1] - C[1]) * (A[0] - C[0]) + (C[0] - B[0]) * (A[1] - C[1])
    areaACP = (C[1] - A[1]) * (P[0] - C[0]) + (A[0] - C[0]) * (P[1] - C[1])

    try:
        u = areaPCB / areaABC
        v = areaACP / areaABC
        w = 1 - u - v
    except:
        u = v = w = -1
    return u, v, w


# fun submatrix
def submatrix(matrix, i, j):
    return [row[:j] + row[j+1:] for row in (matrix[:i]+matrix[i+1:])]

# fun cofactor
def cofactor(matrix, i, j):
    return ((-1)**(i+j)) * determinant(submatrix(matrix, i, j))

# fun determinant
def determinant(matrix):
    # base case for 2x2 matrix
    if len(matrix) == 2:
        return matrix[0][0]*matrix[1][1] - matrix[0][1]*matrix[1][0]

    det = 0
    for j in range(len(matrix)):
        det += matrix[0][j] * cofactor(matrix, 0, j)
    return det

# fun transpose
def transpose(matrix):
    return [[matrix[j][i] for j in range(len(matrix))] for i in range(len(matrix[0]))]

# fun inverse
def inverse(matrix):
    det = determinant(matrix)
    # special case for 2x2 matrix:
    if len(matrix) == 2:
        return [[matrix[1][1]/det, -1*matrix[0][1]/det],
                [-1*matrix[1][0]/det, matrix[0][0]/det]]

    # find matrix of cofactors
    cofactors = []
    for r in range(len(matrix)):
        cofactorRow = []
        for c in range(len(matrix)):
            cofactorRow.append(cofactor(matrix, r, c))
        cofactors.append(cofactorRow)
    cofactors = transpose(cofactors)
    for r in range(len(cofactors)):
        for c in range(len(cofactors)):
            cofactors[r][c] = cofactors[r][c] / det
    return cofactors

# fun subvector
def subvector(vector, i):
    return vector[:i] + vector[i+1:]



# fun normal vector
def normalVector(vector):
    magnitud = math.sqrt(sum(x ** 2 for x in vector))

    if magnitud == 0:
        raise ValueError("Error")

    vector_normalizado = [x / magnitud for x in vector]

    return vector_normalizado

def normalize(vector):
    normal_vector = normalVector(vector)
    if not normal_vector:
        return vector
    return [element / normal_vector[i] for i, element in enumerate(vector)]


# fun cross product
def crossProduct(vector1, vector2):
    return [vector1[1]*vector2[2] - vector1[2]*vector2[1],
            vector1[2]*vector2[0] - vector1[0]*vector2[2],
            vector1[0]*vector2[1] - vector1[1]*vector2[0]]

def dot_product(v1, v2):
    return sum(x * y for x, y in zip(v1, v2))


def vectorMagnitude(vector):
    return sum(i ** 2 for i in vector) ** 0.5

def ScalarPerVector(vector, scalar):
    result = [scalar * value for value in vector]
    return result

def VectorReflected(vector, normal):
    dot = dot_product(vector, normal)
    reflection = [2 * dot * normal[i] - vector[i] for i in range(len(vector))]
    return reflection

def InternalReflection(normal, incident, n1, n2):
    c1 = dot_product(normal, incident)

    if (c1 < 0):
        c1 = -c1
    else:
        normal = ScalarPerVector(normal,-1)
        n1, n2 = n2, n1

    if (n1 < n2):
        return False

    tetha1 = math.acos(c1)
    tethaC = math.asin(n2 / n1)

    return tetha1 >= tethaC


def refractVector(normal, incident, n1, n2):
    c1 = newDotProduct(normal, incident)

    if (c1 < 0):
        c1 = -c1
    else:
        normal = ScalarPerVector(normal,-1)
        n1, n2 = n2, n1

    n = n1 / n2

    t1 = ScalarPerVector(NewAddVectors(incident, ScalarPerVector(normal, c1)), n)
    t2 = elementwise_subtract(t1, normal)
    x = (1 - n ** 2 * (1 - c1 ** 2)) ** 0.5
    t = ScalarPerVector(t2, x)

    return normalVector(t)


def fresnel(normal, incident, n1, n2):
    c1 = dot_product(normal, incident)

    if (c1 < 0):
        c1 = -c1
    else:
        normal = ScalarPerVector(normal,-1)
        n1, n2 = n2, n1

    s2 = (n1 * (1 - c1 ** 2) ** 0.5) / n2
    c2 = (1 - s2 ** 2) ** 0.5

    f1 = (((n2 * c1) - (n1 * c2)) / ((n2 * c1) + (n1 * c2))) ** 2
    f2 = (((n1 * c2) - (n2 * c1)) / ((n1 * c2) + (n2 * c1))) ** 2

    kr = (f1 + f2) / 2
    kt = 1 - kr

    return kr, kt

def NewAddVectors(v1, v2):
    if len(v1) != len(v2):
        raise ValueError("Error")

    resultado = [v1[i] + v2[i] for i in range(len(v1))]
    return resultado

def newDotProduct(v1, v2):
    if len(v1) != len(v2):
        raise ValueError("Error")

    resultado = sum(v1[i] * v2[i] for i in range(len(v1)))
    return resultado

def CrossProduct(vector1, vector2):
    if len(vector1) != len(vector2):
        raise ValueError("Los vectores deben tener la misma longitud para el producto cruz.")

    if len(vector1) < 3:
        raise ValueError("El producto cruz solo está definido para vectores tridimensionales (longitud 3).")

    result = [0] * len(vector1)

    for i in range(len(vector1)):
        next_i = (i + 1) % len(vector1)
        next_next_i = (i + 2) % len(vector1)

        result[i] = vector1[next_i] * vector2[next_next_i] - vector1[next_next_i] * vector2[next_i]

    return result

def NewAddVectors(vector1, vector2):
    return [a + b for a, b in zip(vector1, vector2)]


def divTF(t, d):
    if not 0 in d: 
        divided_tuple = tuple(value / divisor for value, divisor in zip(t, d))
        return divided_tuple
    else:
        return t
