[![Python application](https://github.com/rupestre-campos/mapbiomas-vector-extractor/actions/workflows/python-app.yml/badge.svg)](https://github.com/rupestre-campos/mapbiomas-vector-extractor/actions/workflows/python-app.yml)

# Mapbiomas  Vector Extractor
Simple app to upload a geojson and get Mapbiomas (Brazil) data as vector

## Demo app
You can test the demo hosted on streamlit [here](https://mapbiomas-vector-extractor.streamlit.app/).

## Instalation
How to run in debian based linux distros
Recomended Python version: Python 3.10 or above

```
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt

streamlit run src/main.py
```

## Development
How to run tests
```
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt

# install playright browser files
playwright install

# run tests
pytest tests/
```

## Docker build

```
docker build -t mapbiomas-vector-extractor .
docker run -d --name mapbiomas-vector-extractor-container -p 8002:8002 mapbiomas-vector-extractor
docker start mapbiomas-vector-extractor-container
```
