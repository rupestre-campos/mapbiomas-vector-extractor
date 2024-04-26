import io
from PIL import Image
import pytest
import json
import numpy as np
from model.read_cog import ReadCOG
from mapbiomas_classes import mapbiomas_classes
import zipfile
import os

os.environ["GDAL_CACHEMAX"] = "200"
os.environ["GDAL_DISABLE_READDIR_ON_OPEN"] = "EMPTY_DIR"
os.environ["GDAL_HTTP_MULTIPLEX"] = "YES"
os.environ["GDAL_HTTP_MERGE_CONSECUTIVE_RANGES"] = "YES"
os.environ["GDAL_BAND_BLOCK_CACHE"] = "HASHSET"
os.environ["GDAL_HTTP_MAX_RETRY"] = "4"
os.environ["GDAL_HTTP_RETRY_DELAY"] = "0.42"
os.environ["GDAL_HTTP_VERSION"] = "2"
os.environ["CPL_VSIL_CURL_ALLOWED_EXTENSIONS"] = ".tif,.TIF,.tiff"
os.environ["CPL_VSIL_CURL_CACHE_SIZE"] = "200000000"
os.environ["VSI_CACHE"] = "TRUE"
os.environ["VSI_CACHE_SIZE"] = "5000000"
os.environ["PROJ_NETWORK"] = "OFF"

@pytest.fixture
def sample_data_url():
    return "https://storage.googleapis.com/mapbiomas-public/initiatives/brasil/collection_8/lclu/coverage/brasil_coverage_1985.tif"

@pytest.fixture
def feature_geojson():
    with open("tests/data/polygon_feature.geojson") as test_data:
        polygon_geojson = json.load(test_data)
    return {
            "type": "Feature",
            "properties": {},
            "geometry": polygon_geojson
        }

@pytest.fixture
def feature_collection():
    with open("tests/data/polygon_feature.geojson") as test_data:
        polygon_geojson = json.load(test_data)
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {},
                "geometry": polygon_geojson
            }
        ]
    }


def test_init_read_stac():
    stac_reader = ReadCOG()
    assert isinstance(stac_reader, ReadCOG)

def test_render_mapbiomas(feature_geojson, sample_data_url):
    mapbimas_reader = ReadCOG()
    params = {
            "feature_geojson": feature_geojson,
            "src_path": sample_data_url,
            "classes_names": mapbiomas_classes,
            "max_size": None
    }
    polygons = mapbimas_reader.render_mapbiomas_from_cog(params)
    assert isinstance(polygons, type(feature_geojson))

def test_render_mapbiomas_empty(feature_geojson, sample_data_url):
    mapbimas_reader = ReadCOG()
    params = {
            "feature_geojson": None,
            "src_path": sample_data_url,
            "classes_names": mapbiomas_classes,
            "max_size": None
    }
    polygons = mapbimas_reader.render_mapbiomas_from_cog(params)
    assert isinstance(polygons, type(feature_geojson))

def test_area(feature_geojson):
    mapbimas_reader = ReadCOG()
    polygon_area = mapbimas_reader.area_ha(feature_geojson.get("geometry"))
    assert polygon_area == 5.13368
