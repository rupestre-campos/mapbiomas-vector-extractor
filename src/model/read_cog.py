import pyproj
import numpy as np
from rasterio import warp
from rio_tiler.io import COGReader
from rasterio.features import shapes
from rasterio.transform import Affine
from shapely.ops import transform
from shapely.geometry import shape, mapping


class ReadCOG:
    def __init__(self, geographic_crs="EPSG:4326", projected_crs="EPSG:6933", float_precision=6):
        self.default_crs = geographic_crs
        self.float_precision = float_precision
        self.geographic_crs = pyproj.CRS(geographic_crs)
        self.projected_crs = pyproj.CRS(projected_crs)
        self.transform_geo_to_projected = self.__get_geo_transform(geographic_crs, projected_crs)

    @staticmethod
    def __get_geo_transform(origin_crs, destination_crs):
        return pyproj.Transformer.from_crs(origin_crs, destination_crs, always_xy=True).transform

    @staticmethod
    def __tiler(src_path, *args, **kwargs):
        with COGReader(src_path) as cog:
            return cog.feature(*args, **kwargs)

    def __transform_to_meters(self, input_geom):
        return transform(self.transform_geo_to_projected, input_geom)

    def area_ha(self, polygon_geojson):
        polygon = shape(polygon_geojson)
        polygon_meters = self.__transform_to_meters(polygon)
        return round(polygon_meters.area/10_000, self.float_precision)

    def __get_image_bounds(self, image):
        left, bottom, right, top = [round(i,self.float_precision) for i in image.bounds]
        bounds_4326 = warp.transform_bounds(
            src_crs=image.crs,
            dst_crs=self.default_crs,
            left=left,
            bottom=bottom,
            right=right,
            top=top
        )
        bounds_4326 = [round(i, self.float_precision) for i in bounds_4326]
        return [[bounds_4326[1], bounds_4326[0]], [bounds_4326[3], bounds_4326[2]]]

    def get_transform(self, transformed_bounds, width, height):
        min_y, min_x = transformed_bounds[0]
        max_y, max_x = transformed_bounds[1]

        pixel_size_x = round((max_x - min_x) / width, self.float_precision)
        pixel_size_y = round((max_y - min_y) / height, self.float_precision)

        transform = Affine(pixel_size_x, 0.0, min_x,
                           0.0, -pixel_size_y, max_y)
        return transform

    def get_polygons(self, feature_geojson, image, mask, transform, classes_names, year):
        mask_expanded = np.expand_dims(mask, axis=0)

        image_shapes = shapes(image.astype('uint8'), mask=mask_expanded, transform=transform)
        feature_geometry = shape(feature_geojson['geometry'])

        features = []

        for image_shape in image_shapes:
            pixel_value = int(image_shape[1])
            geom = image_shape[0]
            image_geometry = shape(geom)
            intersection = image_geometry.intersection(feature_geometry)

            intersection = mapping(intersection)
            area = self.area_ha(intersection)

            properties = {"pixel_value":pixel_value, "area_ha": area, "year": year}
            properties.update(classes_names[pixel_value])
            feature = {
                "type": "Feature",
                "geometry": intersection,
                "properties": properties
            }
            features.append(feature)

        feat_collection = {
            "type": "FeatureCollection",
            "features": features
        }
        return feat_collection

    def render_mapbiomas_from_cog(self, params):
        feature_geojson = params.get("feature_geojson")
        args = (feature_geojson, )
        if not feature_geojson:
            return {}

        kwargs = {
            "max_size": params.get("max_size"),
        }

        image_data = self.__tiler(params.get("src_path"), *args, **kwargs)
        image_bounds = self.__get_image_bounds(image_data)
        transform = self.get_transform(image_bounds, image_data.width, image_data.height)

        features = self.get_polygons(
            feature_geojson=feature_geojson,
            image=image_data.data,
            mask=image_data.mask,
            transform=transform,
            classes_names=params.get("classes_names"),
            year=params.get("year")
        )

        return features