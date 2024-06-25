import os
from datetime import datetime

class AppConfig:
    def __init__(self):
        self.url_mapbiomas = os.getenv("URL_MAPBIOMAS", "https://storage.googleapis.com/mapbiomas-public/initiatives/brasil/collection_8/lclu/coverage")
        self.url_mapbiomas_legend = os.getenv("URL_MAPBIOMAS_LEGEND", "https://brasil.mapbiomas.org/wp-content/uploads/sites/4/2023/08/Legenda-Colecao-8-LEGEND-CODE.pdf")
        self.mapbiomas_start_year = int(os.getenv("MAPBIOMAS_START_YEAR", "1985"))
        self.mapbiomas_end_year = int(os.getenv("MAPBIOMAS_END_YEAR", "2022"))
        self.max_polygon_clip_area_ha = float(os.getenv("MAX_POLYGON_CLIP_AREA_HA", "30000"))
        self.float_precision = int(os.getenv("FLOAT_PRECISION", 6))
        self.map_feature_atributes = os.getenv("MAP_FEATURE_ATRIBUTES", "class_type,class_name,area_ha,pixel_value").split(",")
        self.map_feature_atributes_alias = os.getenv("MAP_FEATURE_ATRIBUTES_ALIAS", "Type,Name,Area (ha),Pixel Value").split(",")
        self.open_street_maps = os.getenv("OSM_BASEMAP", "https://tile.openstreetmap.org/{z}/{x}/{y}.png")
        self.google_basemap = os.getenv("GOOGLE_BASEMAP", "https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}")
        self.esri_basemap = os.getenv("ESRI_BASEMAP", "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}")