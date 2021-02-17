import jaydebeapi
import subprocess

# Connection param
username='<username>'
password='<password>'
host='<hostname or ip>'
port='<port(21050)>'
db='<database>'
krbfqdn='<krbfqdn>'
realm='<realm>'

# Connection param
driver = 'com.cloudera.impala.jdbc41.Driver'
url = f'jdbc:impala://{host}:{port}/{db}'
driver_arg = {
    'AuthMech': '1'
    ,'Host': f'{host}'
    ,'Port': f'{port}'
    ,'KrbHostFQDN': f'{krbfqdn}'
    ,'KrbRealm': f'{realm}'
    ,'KrbServiceName': 'impala'}
jarFile = [
    '/tmp/jars/commons-codec-1.3.jar'
    ,'/tmp/jars/commons-logging-1.1.1.jar'
    ,'/tmp/jars/hive_metastore.jar'
    ,'/tmp/jars/hive_service.jar'
    ,'/tmp/jars/httpclient-4.1.3.jar'
    ,'/tmp/jars/httpcore-4.1.3.jar'
    ,'/tmp/jars/ImpalaJDBC41.jar'
    ,'/tmp/jars/libfb303-0.9.0.jar'
    ,'/tmp/jars/libthrift-0.9.0.jar'
    ,'/tmp/jars/log4j-1.2.14.jar'
    ,'/tmp/jars/ql.jar'
    ,'/tmp/jars/slf4j-api-1.5.11.jar'
    ,'/tmp/jars/slf4j-log4j12-1.5.11.jar'
    ,'/tmp/jars/TCLIServiceClient.jar'
    ,'/tmp/jars/zookeeper-3.4.6.jar']

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