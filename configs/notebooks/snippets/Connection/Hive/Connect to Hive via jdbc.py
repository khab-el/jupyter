import jaydebeapi
import subprocess

# Connection param
username='<username>'
password='<password>'
host='<hostname or ip>'
port='<port(10000)>'
db='<database>'
krbfqdn='<krbfqdn>'
realm='<realm>'

# Connection param
driver = 'com.cloudera.hive.jdbc41.HS2Driver'
url = f'jdbc:hive2://{host}:{port}/{db}'
driver_arg = {
    'tez.queue.name': 'users',
    'AuthMech': '1',
    'Host': f'{host}',
    'Port': f'{port}',
    'KrbHostFQDN': f'{krbfqdn}',
    'KrbRealm': f'{realm}',
    'KrbServiceName': 'hive'}
jarFile = ['/tmp/jars/HiveJDBC41.jar']

def krbauth(username, password):
    realm=f'@{realm}'
    cmd = ['kinit', '-c', '/tmp/krb5cc_1000', username+realm]
    success = subprocess.run(cmd, input=password.encode(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode
    return not bool(success)

# Create user's token
if krbauth(username, password):
    print('Succesfully Logged in!')
else:
    print('Incorrect Login!')

# Create connection
conn = jaydebeapi.connect(
    jclassname=driver
    ,url=url
    ,driver_args=driver_arg
    ,jars=jarFile)

# Get cursor to interact with the SQL engine
cursor = conn.cursor()

# Execute queries like so:
cursor.execute("SHOW TABLES;")

result = cursor.fetchall()

# Remember to always close your connection once done, otherwise unexpected behavior may result!
conn.close()