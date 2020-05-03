FROM python:2.7-slim-buster

COPY . /app
WORKDIR /app

RUN pip install --upgrade pip \
    && pip install numpy \
    && pip install pandas \
    && pip install geopandas \
    && pip install bokeh

EXPOSE 5006 
CMD bokeh serve covid_map.py --port 5006 --allow-websocket-origin=localhost:5006 
