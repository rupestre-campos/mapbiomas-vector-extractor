import os
from datetime import datetime

class AppConfig:
    def __init__(self):
        self.url_mapbiomas = os.getenv("URL_MAPBIOMAS", "https://storage.googleapis.com/mapbiomas-public/initiatives/brasil/collection_8/lclu/coverage")
        self.url_mapbiomas_legend = os.getenv("URL_MAPBIOMAS_LEGEND", "https://brasil.mapbiomas.org/wp-content/uploads/sites/4/2023/08/Legenda-Colecao-8-LEGEND-CODE.pdf")
        self.mapbiomas_start_year = int(os.getenv("MAPBIOMAS_START_YEAR", "1985"))
        self.mapbiomas_end_year = int(os.getenv("MAPBIOMAS_END_YEAR", "2022"))
        self.max_polygon_clip_area_ha = float(os.getenv("MAX_POLYGON_CLIP_AREA_HA", "1000"))
        self.float_precision = int(os.getenv("FLOAT_PRECISION", 6))