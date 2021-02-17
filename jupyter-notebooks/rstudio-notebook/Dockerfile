ARG BASE_CONTAINER=jupyter/minimal-notebook
FROM $BASE_CONTAINER

LABEL maintainer="Eldar Khabibulin exabib@gmail.com"

USER root

# install odbc pre-requisites
RUN apt-get update -y && \
    apt-get -y install \
	g++ \
	curl \
	telnet \
	ssh \
	unixodbc-dev \
	odbc-postgresql \
	zip

# install mysql for odbc driver
RUN wget https://dev.mysql.com/get/Downloads/Connector-ODBC/8.0/mysql-connector-odbc-8.0.22-linux-glibc2.12-x86-64bit.tar.gz && \
	tar -xvf mysql-connector-odbc-8.0.22-linux-glibc2.12-x86-64bit.tar.gz && \
	cp mysql-connector-odbc-8.0.22-linux-glibc2.12-x86-64bit/lib/libmyodbc* /usr/lib/x86_64-linux-gnu/odbc/ && \
	mysql-connector-odbc-8.0.22-linux-glibc2.12-x86-64bit/bin/myodbc-installer -d -a -n "MySQL" -t "DRIVER=/usr/lib/x86_64-linux-gnu/odbc/libmyodbc8w.so;"

# install hive and impala odbc driver
ADD clouderahiveodbc_2.6.9.1009-2_amd64.deb /tmp/clouderahiveodbc_2.6.9.1009-2_amd64.deb
ADD clouderaimpalaodbc_2.6.11.1011-2_amd64.deb /tmp/clouderaimpalaodbc_2.6.11.1011-2_amd64.deb

RUN apt install -y /tmp/clouderahiveodbc_2.6.9.1009-2_amd64.deb
RUN apt install -y /tmp/clouderaimpalaodbc_2.6.11.1011-2_amd64.deb

COPY cloudera.hiveodbc.ini /opt/cloudera/hiveodbc/lib/64/cloudera.hiveodbc.ini
COPY cloudera.impalaodbc.ini /opt/cloudera/impalaodbc/lib/64/cloudera.impalaodbc.ini

RUN rm -rf mysql-connector-odbc-8.0.22-linux-glibc2.12-x86-64bit.tar.gz && \
    rm -rf mysql-connector-odbc-8.0.22-linux-glibc2.12-x86-64bit

# install new pyhton lib
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

# enable deleting non empty folder
COPY filemanager.py /opt/conda/lib/python3.8/site-packages/notebook/services/contents/filemanager.py

RUN jupyter lab build
RUN jupyter serverextension enable --py jupyterlab_git && \
	jupyter nbextension enable snippets_menu/main

USER root

# R pre-requisites
RUN apt-get install -y --no-install-recommends \
    fonts-dejavu \
    unixodbc \
    unixodbc-dev \
    r-cran-rodbc \
    gfortran \
    gcc && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Fix for devtools https://github.com/conda-forge/r-devtools-feedstock/issues/4
RUN ln -s /bin/tar /bin/gtar

USER $NB_UID

# R packages
RUN conda install --quiet --yes \
    'r-base=4.0.3' \
    'r-caret=6.*' \
    'r-crayon=1.3*' \
    'r-devtools=2.3*' \
    'r-forecast=8.13*' \
    'r-hexbin=1.28*' \
    'r-htmltools=0.5*' \
    'r-htmlwidgets=1.5*' \
    'r-irkernel=1.1*' \
    'r-nycflights13=1.0*' \
    'r-randomforest=4.6*' \
    'r-rcurl=1.98*' \
    'r-rmarkdown=2.5*' \
    'r-rodbc=1.3*' \
    'r-rsqlite=2.2*' \
    'r-shiny=1.5*' \
    'r-tidyverse=1.3*' \
    'unixodbc=2.3.*' \
    'r-tidymodels=0.1*' \
    && \
    conda clean --all -f -y && \
    fix-permissions "${CONDA_DIR}"

USER root

# Install e1071 R package (dependency of the caret R package)
RUN conda install --quiet --yes r-e1071

RUN python -m pip install jupyter-rsession-proxy
RUN pip install jupyter-shiny-proxy
RUN cd /tmp/ && \
    git clone --depth 1 https://github.com/jupyterhub/jupyter-server-proxy && \
    cd jupyter-server-proxy/jupyterlab-server-proxy && \
    npm install && npm run build && jupyter labextension link . && \
    npm run build && jupyter lab build

# install rstudio-server
USER root
RUN apt update -y && apt install libssl-dev -y 
ADD ./rstudio-server-1.2.1335-amd64.deb /tmp/rstudio.deb
RUN apt-get install -y /tmp/rstudio.deb && \
    rm /tmp/rstudio.deb && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
ENV PATH=$PATH:/usr/lib/rstudio-server/bin

# Install shiny package for R
RUN Rscript -e "install.packages('shiny', repos='https://cran.rstudio.com/')"

RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
    default-jdk \
    wget

USER $NB_USER

# R Packages
RUN conda install --quiet --yes \
    'r-rjava'

# By default R fails to find jni.h so we specify the include directory
# manually
RUN R CMD javareconf JAVA_CPPFLAGS=-I/usr/lib/jvm/default-java/include

# Installing RWeka fails unless we set the LD_LIBRARY_PATH to point to
# paths containing libjvm.so
ENV LD_LIBRARY_PATH=/usr/lib/jvm/default-java/jre/lib/amd64/server:/usr/lib/jvm/default-java/jre/lib/amd64

RUN Rscript -e "install.packages('RWeka', repos='https://cran.rstudio.com/')"

USER root
# install shiny server
ADD ./shiny-server-1.5.15.953-amd64.deb /tmp/shiny-server.deb
RUN apt-get install -y /tmp/shiny-server.deb && \
    chmod -R 777 /srv && \
    rm -rf  /tmp/shiny-server.deb

USER $NB_USER