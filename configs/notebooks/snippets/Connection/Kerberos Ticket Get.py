import subprocess

# Connection param
username='<username>'
password='<password>'
realm='<realm>'

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