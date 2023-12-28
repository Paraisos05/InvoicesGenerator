import pandas as pd
import pyodbc  # Necesitas instalar pyodbc para trabajar con SQL Server

# Lee el archivo CSV en un DataFrame
df = pd.read_csv('mod3.csv')

# Conecta con tu base de datos SQL Server
conn = pyodbc.connect(
    'Driver={SQL Server};'
    'Server=localhost;'
    'Database=AssuremPro-bak27Dec2023;'
    'Trusted_Connection=yes;'
)

# Consulta la base de datos para obtener los valores de COMPANY
query = " Select COMPANY from CONTACT; "  # Reemplaza con la consulta adecuada
company_values = pd.read_sql_query(query, conn)

# Suplanta los valores en la columna "from_who" con los valores de "COMPANY"
df['from_who'] = company_values['COMPANY']

# Guarda el DataFrame modificado en un nuevo archivo CSV
df.to_csv('archivo_modificado.csv', index=False)

# Cierra la conexión a la base de datos
conn.close()
