import pytest
import json
from mapbiomas_classes import mapbiomas_classes
from controller.polygon_renderer import PolygonRenderer
from app_config import AppConfig

app_config_data = AppConfig()

@pytest.fixture
def sample_data_url():
    return f"{app_config_data.url_mapbiomas}/brasil_coverage_1985.tif"

@pytest.fixture
def feature_geojson():
    with open("tests/data/polygon_feature.geojson") as test_data:
        return json.load(test_data)

@pytest.fixture
def big_feature_geojson():
    with open("tests/data/big_polygon.geojson") as test_data:
        return json.load(test_data)


def test_init_read_stac():
    image_renderer = PolygonRenderer()
    assert isinstance(image_renderer, PolygonRenderer)

def test_render_mapbiomas(mocker, feature_geojson, sample_data_url):
    mocker.patch(
        "model.read_cog.ReadCOG.render_mapbiomas_from_cog",
        return_value=feature_geojson
    )
    polygon_renderer = PolygonRenderer()
    params = {
            "feature_geojson": {"geometry":feature_geojson},
            "src_path": sample_data_url,
            "classes_names": mapbiomas_classes,
            "max_size": None
    }

    polygons = polygon_renderer.render_mapbiomas(params)
    assert isinstance(polygons, type(feature_geojson))

def test_render_mapbiomas_error(mocker, big_feature_geojson, sample_data_url):
    mocker.patch(
        "model.read_cog.ReadCOG.render_mapbiomas_from_cog",
        return_value=feature_geojson
    )
    polygon_renderer = PolygonRenderer()
    params = {
            "feature_geojson": {"geometry":big_feature_geojson},
            "src_path": sample_data_url,
            "classes_names": mapbiomas_classes,
            "max_size": None
    }

    polygons = polygon_renderer.render_mapbiomas(params)
    assert "error" in polygons
