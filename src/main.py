import streamlit as st
from io import StringIO
import json
from app_config import AppConfig
from controller.polygon_renderer import PolygonRenderer
from mapbiomas_classes import mapbiomas_classes

app_config_data = AppConfig()

st.set_page_config(
    page_title="Mapbiomas Vector Extractor",
    page_icon=":world_map:",
)

worker_image_renderer = PolygonRenderer()

@st.cache_data
def mapbiomas_clip(image_url,feature_geojson):
    params = {
        "src_path": image_url,
        "feature_geojson": feature_geojson.get("features")[0],
        "classes_names": mapbiomas_classes,
        "max_size": None
    }

    polygons = worker_image_renderer.render_mapbiomas(params)
    if "error" in polygons:
        st.write(
            f"Polygon area ({polygons.get('area_ha')}ha) must be smaller than {app_config_data.max_polygon_clip_area_ha}ha")
        return {}

    return polygons

def create_download_button(polygons_data, name, file_name):
    file_name_sufix = file_name.split(".")[0]
    st.download_button(
        label="Download vector data",
        data = json.dumps(polygons_data, indent=4, ensure_ascii=False),
        file_name = f"mapbiomas_{name}_{file_name_sufix}.geojson",
        mime="application/geojson"
    )

def main():
    st.title("Mapbiomas Vector Extractor")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write("Upload your polygon as .geojson to get mapbiomas data as vector")
        st.write(f"Maximum area allowed: {app_config_data.max_polygon_clip_area_ha}ha")
    with col3:
        st.write("[Code on GitHub](https://github.com/rupestre-campos/mapbiomas-vector-extractor)")

    uploaded_file = st.file_uploader("Choose a geojson file", type="geojson")

    years = [year for year in range(app_config_data.mapbiomas_start_year, app_config_data.mapbiomas_end_year+1)]
    years = sorted(years, reverse=True)
    year_selected = st.selectbox("Select year", options=years)

    url_year = f"{app_config_data.url_mapbiomas}/brasil_coverage_{year_selected}.tif"
    with st.expander("Links to raw data"):
        st.write(f"[Download complete raster data]({url_year})")
        st.write(f"[Download legend]({app_config_data.url_mapbiomas_legend})")

    if uploaded_file is not None:
        stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
        string_data = stringio.read()
        geometry = json.loads(string_data)
        polygons = mapbiomas_clip(
            url_year,
            geometry)

        if polygons:
            create_download_button(polygons, year_selected, uploaded_file.name)

    return True

if __name__ == "__main__":
    main()