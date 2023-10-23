import os

# Especifica la ruta de la carpeta que deseas explorar
ruta_carpeta = './img'

# Lista los directorios en la carpeta especificada
directorios = [nombre for nombre in os.listdir(ruta_carpeta) if os.path.isdir(os.path.join(ruta_carpeta, nombre))]

# Imprime la lista de directorios
for directorio in directorios:
    print(directorio)
