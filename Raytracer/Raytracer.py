import pygame as pg
from pygame.locals import *
from rt import Raytracer
from figures import *
from materials import *
from lights import *

import time

width = 1080
height = 720

pg.init()

screen = pg.display.set_mode((width, height), pg.DOUBLEBUF | pg.HWACCEL | pg.HWSURFACE)
screen.set_alpha(None)

background_image = pg.image.load('./img/planet.webp')  # Cambia 'ruta_de_tu_imagen_de_fondo.jpg' a la ruta correcta de tu imagen
#background_image = pg.transform.scale(background_image, (width, height))  # Escala la imagen al tamaño de la ventana

raytracer = Raytracer(screen=screen)

raytracer.envMap = background_image

metal = Material(diffuse=(0.1, 0.1, 0.1), specular=32, ks=0.2, ior=3, matType=REFLECTIVE)
black_cristal = Material(diffuse=(0, 0, 0), specular=64, ks=0.2, ior=1.1, matType=REFLECTIVE)
skyBlue_cristal = Material(diffuse=(0, 0.5, 1), specular=64, ks=0.2, ior=1.1, matType=REFLECTIVE)
opaqueMetalic = Material(diffuse=(0.1, 0.1, 0.1), specular=32, ks=0.2, ior=3, matType=OPAQUE)
cube_txr = Material(texture=pg.image.load('./Textures/cube.jpg'))
planeta_txr = Material(texture=pg.image.load('./Textures/planet_txr.jpg'))
spacial_egg =Material(diffuse=(0.6, 0.6, 0.6), specular=32, ks=0.2, ior=3, matType=TRANSPARENT)
ecubadora = Material(diffuse=(1, 1, 1), specular=32, ks=0.2, ior=3, matType=TRANSPARENT)
luna_txr = Material(texture=pg.image.load('./Textures/luna.jpg'))
mountain_txr = Material(texture=pg.image.load('./Textures/mountain_txr.jpg'))
volcan = Material(texture=pg.image.load('./Textures/volcan.jpg'))

back = Material(diffuse=(0.9, 0.9, 0.9), specular=32, ks=0.2, ior=3, matType=OPAQUE)
white = Material(diffuse=(1, 1, 1), specular=32, ks=0.2, ior=1.1, matType=OPAQUE)
mirror = Material(diffuse=(0.1, 0.1, 0.1), specular=64, ks=0.2, ior=3, matType=REFLECTIVE)

skyblue = (0, 0.5, 1)



# Structuras
sizeDim = 1
raytracer.scene.append(AABB(position=(-3,-2,-6), size=(sizeDim*2.5,sizeDim*2,sizeDim*2.5), material=cube_txr))
raytracer.scene.append(AABB(position=(-0.6,-2,-6), size=(sizeDim*2.5,sizeDim*2,sizeDim*2.5), material=cube_txr))
raytracer.scene.append(AABB(position=(2,-2,-6), size=(sizeDim*2.5,sizeDim*2,sizeDim*2.5), material=cube_txr))
# For structuras hacia atras
atras = 0
x = 0
for i in range(1,5):
    raytracer.scene.append(AABB(position=(2,-2, -6 - (2.5*i+0.3)), size=(sizeDim*2.5,sizeDim*2,sizeDim*2.5), material=cube_txr))
    atras = -6 - (2.5*i+0.3)

for i in range(1,5):
    raytracer.scene.append(AABB(position=(2+(2.5*i+0.3),-2, atras ), size=(sizeDim*2.5,sizeDim*2,sizeDim*2.5), material=cube_txr))
    x = 2+(2.5*i+0.3)

for i in range(1,5):
    raytracer.scene.append(AABB(position=(x,-2, atras - (2.5*i+0.3)), size=(sizeDim*2.5,sizeDim*2,sizeDim*2.5), material=cube_txr))


# Omni
raytracer.scene.append(Sphere((-1.80, 0.25, -5), 0.25, opaqueMetalic))
raytracer.scene.append(Sphere((-1.80, 0.75, -5), 0.25, black_cristal))
raytracer.scene.append(OvalSphere((-1.75, 0.5, -5), 0.75, 0.25, metal))

# Piramide
raytracer.scene.append(Triangle(skyBlue_cristal, (12, -0.5, -25), (10, 0, -25), (12.5, 15, -25)))
raytracer.scene.append(Triangle(skyBlue_cristal, (12, -0.5, -25), (15, -0.25, -25), (12.5, 15, -25)))
raytracer.scene.append(OvalSphere((12.5, 3, -25), 0.5, 0.8, skyBlue_cristal))

#Planeta
raytracer.scene.append(Sphere((25, 20, -75), 15, planeta_txr))

#Luna
raytracer.scene.append(Sphere((-30, 25, -75), 5, luna_txr))

# volcan
raytracer.scene.append(Triangle(volcan, (-30, -10, -50), (30, -10, -50), (0, 35, -50)))

# Montaña
raytracer.scene.append(Triangle(mountain_txr, (-35, -10, -55), (-5, -20, -55), (-10, 35, -55)))


raytracer.lights.append(AmbientLight(0.4))
raytracer.lights.append(DirectionalLight(direction=(-1, -1, -1)))
#raytracer.lights.append(PointLight(point=(2, 1, -5)))



isRunning = True
start_time = time.time()
while isRunning:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            isRunning = False
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                isRunning = False
            elif event.key == pg.K_s:
                pg.image.save(screen, "image.bmp")
    
    raytracer.rtClear()
    raytracer.rtRender()
    
    pg.display.flip()

end_time = time.time()  # Registra el tiempo de finalización al final de la renderización
elapsed_time = end_time - start_time  # Calcula el tiempo transcurrido
print(f"Tiempo de renderizado: {elapsed_time:.2f} segundos")  # Imprime el tiempo de renderizado al final

pg.quit()
