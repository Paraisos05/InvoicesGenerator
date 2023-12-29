import pandas as pd
import pyodbc

# Read the CSV file into a DataFrame
df = pd.read_csv('11_07_2023-61900002XL07.csv')

# Define a function to get FULL_NAME, EMAIL, and DATABASE_NAME based on tracking_number
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

# Create new columns to store FULL_NAME, EMAIL, and DATABASE_NAME
df['FULL_NAME'] = ''
df['EMAIL'] = ''
df['DATABASE_NAME'] = ''

# Define connection strings and corresponding database names
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
    # Add connection strings and database names for the other databases here
]

# Loop through each row in the DataFrame
for index, row in df.iterrows():
    tracking_number = row['AIRBILL #']  # Replace 'AIRBILL #' with your actual column name
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
            break  # Exit the loop once data is found from one database

# Save the updated DataFrame to a new CSV file
df.to_csv('your_output.csv', index=False)
