ARG BASE_CONTAINER=khabel/scipy-notebook
FROM $BASE_CONTAINER

USER root

RUN pip install \
        gensim \
        nltk \
        spacy \
        fasttext \
        pymorphy2 \
        pymorphy2-dicts \
        imbalanced-learn \
        xgboost \
        lightgbm \
        catboost \
        opencv-python \
        transformers==2.5.1 \
	protobuf==3.12.0

LABEL maintainer="Jupyter Project feat. Danila Slepov"
# Install Tensorflow & Pytorch & Torchvision and google-api
RUN pip install --quiet --no-cache-dir \
    'tensorflow==2.2.0' \
#    'torch==1.6.0+cpu' \
    torch \
    torchvision \
#'torchvision==0.7.0+cpu' \
    'google-api-python-client==1.12.*' \
    && \
    fix-permissions "${CONDA_DIR}" && \
    fix-permissions "/home/${NB_USER}"

USER $NB_UID
