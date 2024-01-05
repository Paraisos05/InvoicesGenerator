import pandas as pd
from io import StringIO

# Lee el contenido del archivo CSV en una cadena (reemplaza 'tu_archivo.csv' con la ruta a tu archivo)
with open('archiSinComillas.csv', 'r') as file:
    csv_content = file.read()

# Divide el contenido en líneas
lines = csv_content.split('\n')

# Lista para almacenar las líneas corregidas
corrected_lines = []

# Itera a través de las líneas y corrige las columnas adicionales
for line in lines:
    # Divide la línea en columnas
    columns = line.split(',')
    
    # Verifica si la línea tiene más columnas de las esperadas
    if len(columns) > 74:
        # Elimina las columnas adicionales (en este caso, eliminamos desde la columna 75 en adelante)
        corrected_line = ','.join(columns[:74])
    else:
        # Si no hay columnas adicionales, la línea se mantiene igual
        corrected_line = line
    
    # Agrega la línea corregida a la lista
    corrected_lines.append(corrected_line)

# Une las líneas corregidas en una cadena nuevamente
corrected_csv_content = '\n'.join(corrected_lines)

# Crea un objeto StringIO a partir de la cadena corregida
csv_io = StringIO(corrected_csv_content)

# Lee el CSV corregido con pandas
df = pd.read_csv(csv_io)

# Ahora puedes trabajar con el DataFrame df que contiene el archivo CSV sin columnas adicionales
