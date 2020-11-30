from ubuntu:18.04

FROM python:3.6.6-slim
RUN pip install --upgrade pip
RUN python -m pip install \ flask \ turicreate \ pandas \ scikit-learn  
RUN python -m pip install \ regex \ unidecode \ numpy \ scipy \ spacy \ beautifulsoup4
RUN python -m pip install --upgrade nltk
WORKDIR /API

COPY . /API

EXPOSE 80

ENTRYPOINT ["python"]
CMD ["api.py"]