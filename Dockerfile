ARG JUPYTERHUB_VERSION=0.9.2
FROM jupyterhub/jupyterhub:$JUPYTERHUB_VERSION

RUN apt update -y && \
    apt install -y gcc krb5-user python3-dev krb5-multidev
RUN pip install --no-cache dockerspawner
RUN pip install --no-cache \
    jupyterhub-dummyauthenticator \
    jupyterhub-ldapauthenticator \
    jupyterhub-kerberosauthenticator \
    jupyterhub-idle-culler \
    PyCryptodome \
    ldap3 \
    bs4
RUN python -m pip install --upgrade pip setuptools wheel
RUN pip install --upgrade ipython-sql psycopg2-binary sqlalchemy sql_magic
RUN pip install jupyter_contrib_nbextensions && jupyter contrib nbextension install 
# load configuration
ADD ./jupyterhub_config.py /srv/jupyterhub/jupyterhub_config.py
