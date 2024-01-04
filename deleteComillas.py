import csv
import re

# Nombre del archivo CSV de entrada y salida
archivo_entrada = 'test6.csv'
archivo_salida = 'archivo_sin_comillas.csv'

# Abrir el archivo de entrada en modo lectura y el archivo de salida en modo escritura
with open(archivo_entrada, 'r', newline='') as csv_entrada, open(archivo_salida, 'w', newline='') as csv_salida:
    # Leer todo el contenido del archivo de entrada
    contenido = csv_entrada.read()
    
    # Eliminar todas las instancias de comillas dobles (") dentro del contenido
    contenido_sin_comillas = contenido.replace('"', '')
    
    # Escribir el contenido sin comillas en el archivo de salida
    csv_salida.write(contenido_sin_comillas)

print(f'Se han eliminado todas las comillas dentro de "{archivo_entrada}" y se ha guardado en "{archivo_salida}".')




## import csv
## import re

# Nombre del archivo CSV de entrada y salida
# archivo_entrada = 'test6.csv'
# archivo_salida = 'archivo_sin_comillas.csv'

# Abrir el archivo de entrada en modo lectura y el archivo de salida en modo escritura
# with open(archivo_entrada, 'r', newline='') as csv_entrada, open(archivo_salida, 'w', newline='') as csv_salida:
    # Leer todo el contenido del archivo de entrada
  #  contenido = csv_entrada.read()
    
    # Eliminar las comillas iniciales y finales de cada fila utilizando expresiones regulares
  #  contenido_sin_comillas = re.sub(r'^"|"$', '', contenido, flags=re.MULTILINE)
    
    # Escribir el contenido sin comillas en el archivo de salida
   # csv_salida.write(contenido_sin_comillas)

# print(f'Se han eliminado las comillas que rodean las filas en "{archivo_entrada}" y se ha guardado en "{archivo_salida}".')
