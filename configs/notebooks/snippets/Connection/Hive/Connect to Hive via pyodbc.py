import subprocess
import pyodbc
import pandas

# Connection param
username='<username>'
password='<password>'
realm='<realm>'

def krbauth(username, password):
    realm=f'@<realm>'
    cmd = ['kinit', '-c', '/tmp/krb5cc_1000', username+realm]
    success = subprocess.run(cmd, input=password.encode(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode
    return not bool(success)

def as_pandas_DataFrame(cursor):
    names = [metadata[0] for metadata in cursor.description]
    return pandas.DataFrame([dict(zip(names, row)) for row in cursor], columns=names)

# Create user's token
if krbauth(username, password):
    print('Succesfully Logged in!')
else:
    print('Incorrect Login!')

# Create connection
pyodbc.autocommit = True
conn = pyodbc.connect("DSN=Cloudera Hive 64-bit", autocommit=True)

# Get cursor to interact with the SQL engine
cursor = conn.cursor()

# Execute queries like so:
cursor.execute("SHOW TABLES;")

# Convert result set into pandas DataFrame
df = as_pandas_DataFrame(cursor)

# Remember to always close your connection once done, otherwise unexpected behavior may result!
conn.close()