import os
import sys
import pwd, grp
import subprocess
import shutil
import datetime
import base64
import hashlib
from Crypto.Cipher import AES
from Crypto import Random
from dockerspawner import SwarmSpawner
from ldap3 import Server, Connection, ALL
from bs4 import BeautifulSoup

class AESCipher(object):
    def __init__(self, key):
        self.block_size = AES.block_size
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, plain_text):
        plain_text = self.__pad(plain_text)
        iv = Random.new().read(self.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        encrypted_text = cipher.encrypt(plain_text.encode())
        return b64encode(iv + encrypted_text).decode("utf-8")

    def decrypt(self, encrypted_text):
        encrypted_text = b64decode(encrypted_text)
        iv = encrypted_text[:self.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        plain_text = cipher.decrypt(encrypted_text[self.block_size:]).decode("utf-8")
        return self.__unpad(plain_text)

    def __pad(self, plain_text):
        number_of_bytes_to_pad = self.block_size - len(plain_text) % self.block_size
        ascii_string = chr(number_of_bytes_to_pad)
        padding_str = number_of_bytes_to_pad * ascii_string
        padded_plain_text = plain_text + padding_str
        return padded_plain_text

    @staticmethod
    def __unpad(plain_text):
        last_character = plain_text[len(plain_text) - 1:]
        return plain_text[:-ord(last_character)]

## Encryption key from env var
key = os.getenv('AES_KEY')

## Init aes method
aes = AESCipher(key)

c.ConfigurableHTTPProxy.should_start = True

## Vars
timestamp = datetime.datetime.utcnow().strftime('%Y%m%d_%H-%M-%S')
notebook_dir = '/home/jovyan/work'
notebook_conf = '/srv/jupyterhub/notebooks'

## Postgresql params
POSTGRES_HOST = 'db'
POSTGRES_PORT = '5432'
POSTGRES_USER = 'hub'
POSTGRES_PASSWORD = aes.decrypt('UnVUa3fmxluaCYCEHfHtAa/1t+LIh3WlD2pBs55MiYI=')
POSTGRES_DB = 'hub'

## After this time notebook will be terminate
inactivity_timeout_terminate=30*60*100

## Available nootebook images that user can select with name in ui
notebook_images = {
        'khabel/base-notebook': 'analytics-base-cpu (Python3)',
        'khabel/scipy-notebook': 'datascience-adv-cpu (Python3)',
        'khabel/deepln-notebook': 'deeplearning-cpu (Tensorflow+Pytorch)'}

## Ldap params configuration
ad_address = '10.80.0.5'
search_user = 'cn=ldapadm,dc=ldap,dc=kernelboot,dc=local'
search_password = aes.decrypt('6bPnRsDnZUYvVo8TLfstLc1gmmh9rJvjuF6m6rSeD1Y=')
user_search_base = 'dc=ldap,dc=kernelboot,dc=local'
# admin group from ldap
admin_group = 'cn=datalab_admin,ou=Groups,dc=ldap,dc=kernelboot,dc=local'
# lead of data scientist group from ldap
ds_lead_group = 'cn=datalab_lead_ds,ou=Groups,dc=ldap,dc=kernelboot,dc=local'
# data scientist group from ldap
ds_group = 'cn=datalab_ds,ou=Groups,dc=ldap,dc=kernelboot,dc=local'
# analytics group from ldap
analyst_group = 'cn=datalab_analyst,ou=Groups,dc=ldap,dc=kernelboot,dc=local'

## Ldap groups that can auth in jupyterhub (you can add more groups, but available list cpu and ram is 1 core and 4 GB)
ad_groups = [
    admin_group
    ,ds_lead_group
    ,ds_group
    ,analyst_group
    ,'cn=datalab_sec_admin,ou=Groups,dc=ldap,dc=kernelboot,dc=local'
    ,'cn=datalab_controller-SVA,ou=Groups,dc=ldap,dc=kernelboot,dc=local'
    ,'cn=datalab_controller-DKK,ou=Groups,dc=ldap,dc=kernelboot,dc=local'
    ]

## List of number of cores available for admin and ds group from ldap
admin_cpu_lst = [1,2,3,4]
ds_lead_cpu_lst = [1,2,3,4]
ds_cpu_lst = [1,2,3,4]
analyst_cpu_lst = [1,2,3,4]

## List of ram in GB available for admin and ds group from ldap
admin_ram_lst = [2,4,6,8]
ds_lead_ram_lst = [2,4,6,8]
ds_ram_lst = [2,4,6,8]
analyst_ram_lst = [2,4,6,8]

class Spawner(SwarmSpawner):
    def _options_form_default(self):
        username = self.user.name
        group_lst = getadgroup(username, ad_address, search_user, search_password, user_search_base, ad_groups)

        soup = BeautifulSoup(f"""
            <label for="stack">{username}, выберете желаемый стек: </label>
            <select name="stack" size="1">
            </select><br>
            <label for="cpu">Выберете желаемое количество ядер: </label>
            <select name="cpu" size="1">
            </select><br>
            <label for="memory">Выберете желаемое количество оперативной памяти: </label>
            <select name="memory" size="1">
            </select>
            """)

        for item in soup.find_all('select', {"name": "stack"}):
            notebooks = ''
            for k, v in notebook_images.items():
                    notebooks += f'<option value="{k}">{v}</option>'
            tags = BeautifulSoup(notebooks)
            item.append(tags)

        for item in soup.find_all('select', {"name": "cpu"}):
            if admin_group in group_lst:
                cpu_lst = ''
                for i in admin_cpu_lst:
                    cpu_lst += f'<option value="{i}">{i} Core</option>'
                tags = BeautifulSoup(cpu_lst)
                item.append(tags)
            elif admin_group not in group_lst:
                cpu_lst = ''
                if ds_lead_group in group_lst:
                    for i in ds_lead_cpu_lst:
                        cpu_lst += f'<option value="{i}">{i} Core</option>'
                    tags = BeautifulSoup(cpu_lst)
                    item.append(tags)
                elif ds_group in group_lst:
                    for i in ds_cpu_lst:
                        cpu_lst += f'<option value="{i}">{i} Core</option>'
                    tags = BeautifulSoup(cpu_lst)
                    item.append(tags)
                elif analyst_group in group_lst:
                    for i in analyst_cpu_lst:
                        cpu_lst += f'<option value="{i}">{i} Core</option>'
                    tags = BeautifulSoup(cpu_lst)
                    item.append(tags)
            else:
                tags = BeautifulSoup('<option value="1">1 Core</option>')
                item.append(tags)

        for item in soup.find_all('select', {"name": "memory"}):
            if admin_group in group_lst:
                ram_lst = ''
                for i in admin_ram_lst:
                    ram_lst += f'<option value="{i}G">{i} GB</option>'
                tags = BeautifulSoup(ram_lst)
                item.append(tags)
            elif admin_group not in group_lst:
                ram_lst = ''
                if ds_lead_group in group_lst:
                    for i in ds_lead_ram_lst:
                        ram_lst += f'<option value="{i}G">{i} GB</option>'
                    tags = BeautifulSoup(ram_lst)
                    item.append(tags)
                elif ds_group in group_lst:
                    for i in ds_ram_lst:
                        ram_lst += f'<option value="{i}G">{i} GB</option>'
                    tags = BeautifulSoup(ram_lst)
                    item.append(tags)
                elif analyst_group in group_lst:
                    for i in analyst_ram_lst:
                        ram_lst += f'<option value="{i}G">{i} GB</option>'
                    tags = BeautifulSoup(ram_lst)
                    item.append(tags)
            else:
                tags = BeautifulSoup('<option value="4G">4 GB</option>')
                item.append(tags)
        return str(soup)

    def options_from_form(self, formdata):
        options = {}
        options['stack'] = formdata['stack']
        container_image = ''.join(formdata['stack'])
        print("SPAWN: " + container_image + " IMAGE" )
        self.container_image = container_image
        options = {}
        options['cpu'] = formdata['cpu']
        container_cpu = ''.join(formdata['cpu'])
        print("SPAWN: " + container_cpu + " cpu" )
        self.cpu_limit = float(container_cpu)
        options = {}
        options['memory'] = formdata['memory']
        container_memory = ''.join(formdata['memory'])
        print("SPAWN: " + container_memory + " memory" )
        self.mem_limit = container_memory
        return options


## Create user dir if doesnt exist and mount it with configs in user'ss notebook
def create_homedir_hook(spawner):
    username = spawner.user.name  # get the username
    volume_path = os.path.join('/storage/nfs', username)
    if not os.path.exists(volume_path):
        os.mkdir(volume_path, 0o755)
        os.chown(volume_path,1000,100)
    mounts_user = [
                    {'type': 'bind',
                    'source': f'/storage/nfs/{username}',
                    'target': notebook_dir, },
                    {'type': 'bind',
                    'source': '/storage/nfs/share',
                    'target': f'{notebook_dir}/share', },
                    {'type': 'bind',
                    'source': '/storage/nfs/mlflow/mlruns',
                    'target': f'{notebook_dir}/mlruns', },
                    {'type': 'bind',
                    'source': f'{notebook_conf}/snippets',
                    'target': '/home/jovyan/work/.local/share/jupyter/snippets', },
                    {'type': 'bind',
                    'source': f'{notebook_conf}/odbcinst.ini',
                    'target': '/etc/odbcinst.ini', },
                    {'type': 'bind',
                    'source': f'{notebook_conf}/odbc.ini',
                    'target': '/etc/odbc.ini', },
                    {'type': 'bind',
                    'source': f'{notebook_conf}/cloudera.hiveodbc.ini',
                    'target': '/opt/cloudera/hiveodbc/lib/64/cloudera.hiveodbc.ini', }, 
                    {'type': 'bind',
                    'source': f'{notebook_conf}/cloudera.impalaodbc.ini',
                    'target': '/opt/cloudera/impalaodbc/lib/64/cloudera.impalaodbc.ini', }, 
                    {'type': 'bind',
                    'source': f'{notebook_conf}/pip.conf',
                    'target': '/etc/pip.conf', },
                    {'type': 'bind',
                    'source': f'{notebook_conf}/custom.js',
                    'target': '/home/jovyan/work/.jupyter/custom/custom.js', },
                    {'type': 'bind',
                    'source': f'{notebook_conf}/krb5.conf',
                    'target': '/etc/krb5.conf', }
                  ]
    ## it's not clear why the above works and alternative mounting approachs do not, but
    ## this is a reliable way to make sure volume mounts work in swarmspawner
    spawner.extra_container_spec = {
        'mounts': mounts_user
    }
    # spawner.environment['SYSGROUPS']=getgroups(username)
    spawner.environment['DB_KEY']=username + 'Pj~FxRHP1@lNFyBCd'

## Need to capture groups - this is an utterly brute force of the `id` command
## this works because we are mounting pam into the jhub front end.
# def getgroups(user):
#     groups=os.popen('/usr/bin/id {}'.format(user)).read()
#     return groups


## Get user's group from ldap
def getadgroup(username, ad_server, search_user, search_password, user_search_base, ad_groups):
    server = Server(ad_server, get_info=ALL)

    conn = Connection(server, search_user, search_password, auto_bind=True)
    conn.search(user_search_base, '(&(objectclass=shadowAccount)(uid='+username+'))', attributes=['memberof'])
    group_list=list(conn.entries[0].memberof)

    return group_list

c.Spawner.pre_spawn_hook = create_homedir_hook
c.Spawner.environment = {'GRANT_SUDO': 'yes'}
c.Spawner.default_url = '/lab'

## LDAPAuth
c.LDAPAuthenticator.server_address = ad_address
c.LDAPAuthenticator.use_ssl = False
c.LDAPAuthenticator.lookup_dn = True
c.LDAPAuthenticator.lookup_dn_search_filter = '({login_attr}={login})'
c.LDAPAuthenticator.lookup_dn_search_user = search_user
c.LDAPAuthenticator.lookup_dn_search_password = search_password
c.LDAPAuthenticator.valid_username_regex = '^.*$'
c.LDAPAuthenticator.user_search_base = user_search_base
c.LDAPAuthenticator.allowed_groups = ad_groups
c.LDAPAuthenticator.user_attribute = 'uid'
c.LDAPAuthenticator.lookup_dn_user_dn_attribute = 'uid'

## JupyterHub
c.JupyterHub.authenticator_class = 'ldapauthenticator.LDAPAuthenticator'
c.JupyterHub.spawner_class = Spawner
c.JupyterHub.hub_ip = '0.0.0.0'
c.JupyterHub.hub_port = 8081
c.JupyterHub.port = 8000
c.JupyterHub.admin_access = True
c.JupyterHub.db_url = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'

## Put the log file in /storage/nfs/logs
c.JupyterHub.extra_log_file = f'/srv/jupyterhub/logs/jupyterhub_{timestamp}.log'

c.JupyterHub.services = [
    {
        'name': 'idle-culler',
        'admin': True,
        'command': [sys.executable, '-m', 'jupyterhub_idle_culler', f'--timeout={inactivity_timeout_terminate}'],
    }
]

## Authenticator
c.Authenticator.admin_users = {'ldapadm'}

## SwarmSpawner
# c.SwarmSpawner.jupyterhub_service_name = "jupyterhubserver"
c.SwarmSpawner.network_name = "dev_hub_network"
c.SwarmSpawner.extra_host_config = { 'network_mode': "dev_hub_network" }
c.SwarmSpawner.remove_containers = True
c.SwarmSpawner.debug = True
c.SwarmSpawner.host_ip = "0.0.0.0"
c.SwarmSpawner.http_timeout = 300
c.SwarmSpawner.start_timeout = 300
c.SwarmSpawner.notebook_dir = notebook_dir

## DockerSpawner
c.DockerSpawner.extra_host_config = {'runtime': 'nvidia'}
# c.DockerSpawner.extra_create_kwargs = {'user': 'root'}
