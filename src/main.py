import json
import folium
import pandas as pd
import geopandas as gpd
import streamlit as st
from io import StringIO
from streamlit_folium import st_folium
from app_config import AppConfig
from controller.polygon_renderer import PolygonRenderer
from mapbiomas_classes import mapbiomas_classes

app_config_data = AppConfig()

st.set_page_config(
    page_title="Mapbiomas Vector Extractor",
    page_icon=":world_map:",
    layout="wide"
)

worker_image_renderer = PolygonRenderer()

@st.cache_data
def mapbiomas_clip(image_url, feature_geojson, year):
    params = {
        "src_path": image_url,
        "feature_geojson": feature_geojson.get("features")[0],
        "classes_names": mapbiomas_classes,
        "max_size": None,
        "year": year
    }

    polygons = worker_image_renderer.render_mapbiomas(params)
    if "error" in polygons:
        st.write(
            f"Polygon area ({polygons.get('area_ha')}ha) must be smaller than {app_config_data.max_polygon_clip_area_ha}ha")
        return {}

    return polygons

def geojson_to_csv(geojson_data):
    properties = [feature["properties"] for feature in geojson_data["features"]]
    df = pd.DataFrame(properties)
    csv_string = df.to_csv(index=False)
    return csv_string

def create_download_button(polygons_data, name, file_name):
    file_name_sufix = file_name.split(".")[0]
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="Download GeoJson",
            data=json.dumps(polygons_data, indent=4, ensure_ascii=False),
            file_name=f"mapbiomas_{name}_{file_name_sufix}.geojson",
            mime="application/geojson"
        )
    with col2:
        csv_data = geojson_to_csv(polygons_data)

        st.download_button(
            label="Download CSV",
            data=csv_data,
            file_name=f"mapbiomas_{name}_{file_name_sufix}.csv",
            mime="text/csv"
        )

def style_function(feature):
    return {
        "fillColor": feature["properties"]["hex_color"],
        "color": feature["properties"]["hex_color"],
        "weight": 1,
        "fillOpacity": 0.6
    }

def highlight_function(feature):
    return  {
        "color": "red",
        "weight": 1.3,
        "fillOpacity": 0
    }

def plot_map(polygons, input_polygon):

    web_map = folium.Map(location=[0, 0], zoom_start=2)

    input_polygon_group = folium.FeatureGroup(name="Input Polygon")
    features_group = folium.FeatureGroup(name="GeoJSON Polygons")

    features = folium.GeoJson(
        polygons,
        style_function=style_function,
        highlight_function=highlight_function,
        tooltip=folium.GeoJsonTooltip(
            fields=app_config_data.map_feature_atributes,
            aliases=app_config_data.map_feature_atributes_alias,
            sticky=False,
            labels=True,
    ),
        popup=folium.GeoJsonPopup(
            fields=app_config_data.map_feature_atributes,
            aliases=app_config_data.map_feature_atributes_alias),
        popup_keep_highlighted=True,
    )

    inverted_coordinates = [(lat, lon) for lon, lat in input_polygon["features"][0]["geometry"]["coordinates"][0]]

    folium.Polygon(
        locations=inverted_coordinates,
        color="red",
        weight=2,
        fill=False,
        fill_opacity=0.0
    ).add_to(input_polygon_group)

    features.add_to(features_group)
    features_group.add_to(web_map)
    input_polygon_group.add_to(web_map)

    bounds = features.get_bounds()
    web_map.fit_bounds(bounds, padding=(30, 30))

    folium.LayerControl().add_to(web_map)

    st_folium(
        web_map,
        use_container_width=True,
        returned_objects=[]
    )

def parse_input_file(string_data):
    try:
        input_json = json.loads(string_data)
        if not "type" in input_json:
            return None
        if input_json.get("type") == "FeatureCollection":
            if len(input_json.get("features",[])) == 0:
                return None
            return {
                "type": "FeatureCollection",
                "features": [input_json.get("features")[0]]
            }
        if input_json.get("type") == "Feature":
            return {
                "type": "FeatureCollection",
                "features": [input_json]
            }
    except Exception as e:
        return None

def main():
    st.title("Mapbiomas Vector Extractor")

    st.write("Upload your polygon as .geojson to get mapbiomas data as vector")
    st.write(f"Maximum area allowed: {app_config_data.max_polygon_clip_area_ha}ha")

    uploaded_file = st.file_uploader("Choose a geojson file", type="geojson")

    years = [year for year in range(app_config_data.mapbiomas_start_year, app_config_data.mapbiomas_end_year+1)]
    years = sorted(years, reverse=True)
    year_selected = st.selectbox("Select year", options=years)
    url_year = f"{app_config_data.url_mapbiomas}/brasil_coverage_{year_selected}.tif"

    if uploaded_file is not None:
        stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
        string_data = stringio.read()
        geometry = parse_input_file(string_data)
        if not geometry:
            st.write("Could not read GeoJson!")
            return False

        polygons = mapbiomas_clip(
            url_year,
            geometry,
            year_selected
        )

        if polygons:
            st.markdown("------------------------------")
            st.markdown(f"## Year: {year_selected}")
            create_download_button(polygons, year_selected, uploaded_file.name)
            col1, col2 = st.columns(2)
            with col1:
                plot_map(polygons, geometry)
            with col2:

                gdf = gpd.GeoDataFrame.from_features(polygons)
                gdf["count"] = 1
                area_per_class = gdf[["count", "area_ha", "class_name"]].groupby("class_name").agg(sum).reset_index().sort_values(by="area_ha", ascending=False)
                # Merge with hex_code from raw gdf
                area_per_class = area_per_class.merge(gdf[["class_name", "hex_color"]].drop_duplicates(), on="class_name")
                area_per_class.rename(columns={"hex_color":"Legend", "class_name":"Class Name", "area_ha":"Area (ha)", "count": "Polygon count"}, inplace=True)
                area_per_class = area_per_class.style.applymap(lambda color: f'background-color: {color}', subset=["Legend"])
                st.dataframe(area_per_class, column_order=["Legend", "Class Name", "Area (ha)", "Polygon count"], hide_index=True)

    with st.expander("Links to raw data"):
        st.write(f"[Download complete raster data]({url_year})")
        st.write(f"[Download legend]({app_config_data.url_mapbiomas_legend})")

    return True

if __name__ == "__main__":
    main()