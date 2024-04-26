from controller.environment_variable_manager import EnvContextManager

from model.read_cog import ReadCOG
from app_config import AppConfig
app_config_data = AppConfig()

class PolygonRenderer:
    def __init__(self,):
        self.cog_reader = self.__model_read_cog()

    @staticmethod
    def __model_read_cog():
        return ReadCOG(float_precision=app_config_data.float_precision)

    def render_mapbiomas(self, params):
        geom = params.get("feature_geojson").get("geometry")
        geom_area = self.cog_reader.area_ha(geom)
        if geom_area > app_config_data.max_polygon_clip_area_ha:
            raise ValueError(f"Polygon area (ha) cannot be greater than {app_config_data.max_polygon_clip_area_ha}")

        return self.cog_reader.render_mapbiomas_from_cog(params)
