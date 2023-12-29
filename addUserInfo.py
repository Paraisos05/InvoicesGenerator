import pandas as pd
import pyodbc

# Read the CSV file into a DataFrame
df = pd.read_csv('11_07_2023-61900002XL07.csv')

# Define a function to get FULL_NAME and EMAIL based on tracking_number
def get_full_name_email(tracking_number, connection_string):
    conn = pyodbc.connect(connection_string)
    sql_query = f"""
    SELECT FULL_NAME, EMAIL
    FROM [USER]
    WHERE USER_ID = (SELECT USER_ID FROM SHIPMENT WHERE TRACKING_NUMBER = '{tracking_number}');
    """
    sql_result = pd.read_sql_query(sql_query, conn)
    conn.close()
    if not sql_result.empty and 'FULL_NAME' in sql_result.columns and 'EMAIL' in sql_result.columns:
        return sql_result.iloc[0]['FULL_NAME'], sql_result.iloc[0]['EMAIL']
    else:
        return None, None  # Return None for both values if no rows found or missing columns

# Create new columns to store FULL_NAME and EMAIL
df['FULL_NAME'] = ''
df['EMAIL'] = ''

# Define connection strings for each database
connection_strings = [
    'Driver={SQL Server};Server=localhost;Database=esurex;Trusted_Connection=yes;',
    'Driver={SQL Server};Server=localhost;Database=AssuremPro-bak27Dec2023;Trusted_Connection=yes;',
    'Driver={SQL Server};Server=localhost;Database=transurit;Trusted_Connection=yes;',
    'Driver={SQL Server};Server=localhost;Database=z2b2;Trusted_Connection=yes;',
    # Add connection strings for the other three databases here
    # Example:
    # 'Driver={SQL Server};Server=another_server;Database=another_database;Trusted_Connection=yes;',
]

# Loop through each row in the DataFrame
for index, row in df.iterrows():
    tracking_number = row['AIRBILL #']  # Replace 'AIRBILL #' with your actual column name
    for connection_string in connection_strings:
        full_name, email = get_full_name_email(tracking_number, connection_string)
        if full_name is not None:
            df.at[index, 'FULL_NAME'] = full_name
            df.at[index, 'EMAIL'] = email
            break  # Exit the loop once data is found from one database

# Save the updated DataFrame to a new CSV file
df.to_csv('your_output.csv', index=False)
