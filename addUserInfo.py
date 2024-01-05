import pandas as pd
import pyodbc
from io import StringIO

# Leer el archivo CSV eliminando las comillas alrededor de cada fila
with open('archiSinComillas.csv', 'r') as file:
    lines = [line.strip('"') for line in file]

# Crear un nuevo DataFrame a partir de las líneas corregidas
df = pd.read_csv(StringIO('\n'.join(lines)))

# Define una función para obtener FULL_NAME, EMAIL y DATABASE_NAME basados en el número de seguimiento
def get_full_name_email(tracking_number, connection_string, database_name):
    conn = pyodbc.connect(connection_string)
    sql_query = f"""
    SELECT FULL_NAME, EMAIL
    FROM [USER]
    WHERE USER_ID = (SELECT USER_ID FROM SHIPMENT WHERE TRACKING_NUMBER = '{tracking_number}');
    """
    sql_result = pd.read_sql_query(sql_query, conn)
    conn.close()
    if not sql_result.empty and 'FULL_NAME' in sql_result.columns and 'EMAIL' in sql_result.columns:
        return sql_result.iloc[0]['FULL_NAME'], sql_result.iloc[0]['EMAIL'], database_name
    else:
        return None, None, None  # Return None for all values if no rows found or missing columns

# Crear nuevas columnas para almacenar FULL_NAME, EMAIL y DATABASE_NAME
df['FULL_NAME'] = ''
df['EMAIL'] = ''
df['DATABASE_NAME'] = ''

# Define cadenas de conexión y nombres de bases de datos correspondientes
connections_info = [
    {
        'connection_string': 'Driver={SQL Server};Server=localhost;Database=esurex;Trusted_Connection=yes;',
        'database_name': 'esurex'
    },
    {
        'connection_string': 'Driver={SQL Server};Server=localhost;Database=AssuremPro-bak27Dec2023;Trusted_Connection=yes;',
        'database_name': 'AssuremPro-bak27Dec2023'
    },
    {
        'connection_string': 'Driver={SQL Server};Server=localhost;Database=transurit;Trusted_Connection=yes;',
        'database_name': 'transurit'
    },
    {
        'connection_string': 'Driver={SQL Server};Server=localhost;Database=z2b2;Trusted_Connection=yes;',
        'database_name': 'z2b2'
    },
    # Agregar cadenas de conexión y nombres de bases de datos para las otras bases de datos aquí
]

# Recorrer cada fila en el DataFrame
for index, row in df.iterrows():
    tracking_number = row['AIRBILL #']  # Reemplazar 'AIRBILL #' con el nombre de columna real
    for connection_info in connections_info:
        full_name, email, database_name = get_full_name_email(
            tracking_number,
            connection_info['connection_string'],
            connection_info['database_name']
        )
        if full_name is not None:
            df.at[index, 'FULL_NAME'] = full_name
            df.at[index, 'EMAIL'] = email
            df.at[index, 'DATABASE_NAME'] = database_name
            break  # Salir del bucle una vez que se encuentren datos en una base de datos

# Guardar el DataFrame actualizado en un nuevo archivo CSV
df.to_csv('tu_output.csv', index=False)
