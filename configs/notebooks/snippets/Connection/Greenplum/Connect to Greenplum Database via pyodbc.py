import pyodbc 
import pandas
import urllib.parse

def as_pandas_DataFrame(cursor):
    names = [metadata[0] for metadata in cursor.description]
    return pandas.DataFrame([dict(zip(names, row)) for row in cursor], columns=names)

# Connection param
host='<hostname>'
db='<database>'
username='<username>'
password=urllib.parse.quote_plus('<password>')

# Create connection
conn = pyodbc.connect('Driver={PostgreSQL};'
                      f'Server={host};'
                      f'Database={db};'
                      f'UID={username};'
                      f'PWD={password}', autocommit=True)

# Get cursor to interact with the SQL engine
cursor = conn.cursor()

# Execute queries like so:
cursor.execute("SELECT version()")

# Convert result set into pandas DataFrame
df = as_pandas_DataFrame(cursor)

# Remember to always close your connection once done, otherwise unexpected behavior may result!
conn.close()