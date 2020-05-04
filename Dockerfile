FROM python:3

COPY . /app
WORKDIR /app

RUN pip install --upgrade pip \
    && pip install numpy \
    && pip install pandas \
    && pip install geopandas \
    && pip install bokeh

