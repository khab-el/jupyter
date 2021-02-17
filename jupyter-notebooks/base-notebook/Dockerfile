ARG BASE_CONTAINER=jupyter/minimal-notebook
FROM $BASE_CONTAINER

USER root

RUN apt-get update -y
RUN apt-get -y install \
	g++ \
	curl \
	telnet \
	ssh \
	unixodbc-dev \
	odbc-postgresql \
	zip

RUN wget https://dev.mysql.com/get/Downloads/Connector-ODBC/8.0/mysql-connector-odbc-8.0.22-linux-glibc2.12-x86-64bit.tar.gz && \
	tar -xvf mysql-connector-odbc-8.0.22-linux-glibc2.12-x86-64bit.tar.gz && \
	cp mysql-connector-odbc-8.0.22-linux-glibc2.12-x86-64bit/lib/libmyodbc* /usr/lib/x86_64-linux-gnu/odbc/ && \
	mysql-connector-odbc-8.0.22-linux-glibc2.12-x86-64bit/bin/myodbc-installer -d -a -n "MySQL" -t "DRIVER=/usr/lib/x86_64-linux-gnu/odbc/libmyodbc8w.so;"

ADD clouderahiveodbc_2.6.9.1009-2_amd64.deb /tmp/clouderahiveodbc_2.6.9.1009-2_amd64.deb
ADD clouderaimpalaodbc_2.6.11.1011-2_amd64.deb /tmp/clouderaimpalaodbc_2.6.11.1011-2_amd64.deb

RUN apt install -y /tmp/clouderahiveodbc_2.6.9.1009-2_amd64.deb
RUN apt install -y /tmp/clouderaimpalaodbc_2.6.11.1011-2_amd64.deb

COPY cloudera.hiveodbc.ini /opt/cloudera/hiveodbc/lib/64/cloudera.hiveodbc.ini
COPY cloudera.impalaodbc.ini /opt/cloudera/impalaodbc/lib/64/cloudera.impalaodbc.ini

RUN python -m pip install --upgrade pip setuptools wheel
RUN pip install \
	jupyter_contrib_nbextensions \
	googletrans==3.0.0 \
	regex \
	pipdeptree \
	pyarrow \
	xlsxwriter \
	pycrypto \
	pyodbc \
	pipreqs \
	ipython-sql \
	psycopg2-binary \
	sqlalchemy \
	sql_magic \
	jaydebeapi \
	jupyterlab-git \
	jupyterlab-snippets 

RUN jupyter contrib nbextension install 

USER $NB_UID

COPY filemanager.py /opt/conda/lib/python3.8/site-packages/notebook/services/contents/filemanager.py

RUN jupyter lab build
RUN jupyter serverextension enable --py jupyterlab_git && \
	jupyter nbextension enable snippets_menu/main

RUN pip install \
        mlflow \
        impala \
        matplotlib \
        seaborn
        
ENV MLFLOW_TRACKING_URI="http://10.80.0.5:5055"

USER root

RUN apt install -y default-jre

COPY jars.tar /tmp/jars.tar

RUN  tar -C /tmp/ -xvf /tmp/jars.tar

USER $NB_USER