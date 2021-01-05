from ubuntu:18.04

FROM python:3.6.6-slim
RUN pip install --upgrade pip
RUN python -m pip install \ flask \ turicreate \ pandas \ scikit-learn \ psycopg2-binary
RUN python -m pip install \ regex \ unidecode \ numpy \ scipy \ spacy \ beautifulsoup4 \ dask
RUN python -m pip install dask[dataframe] --upgrade
RUN python -m pip install --upgrade nltk
WORKDIR /API

COPY . /API

EXPOSE 5000

ENTRYPOINT ["python"]
CMD ["api.py"]
