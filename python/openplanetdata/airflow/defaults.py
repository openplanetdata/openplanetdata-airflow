"""
Shared default constants for OpenPlanetData Airflow workflows.
"""

DOCKER_MOUNT = {"source": "/data", "target": "/data", "type": "bind"}
EMAIL_ALERT_RECIPIENTS = ["airflow@openplanetdata.com"]
GDAL_IMAGE = "ghcr.io/osgeo/gdal:ubuntu-full-3.12.2"
OPENPLANETDATA_IMAGE = "openplanetdata/openplanetdata-airflow:latest"
OPENPLANETDATA_SHARED_DIR = "/data/openplanetdata/shared"
OPENPLANETDATA_WORK_DIR = "/data/openplanetdata"
R2INDEX_CONNECTION_ID = "r2index-openplanetdata-production"
R2_BUCKET = "openplanetdata"

SHARED_PLANET_COASTLINE_GPKG_PATH = f"{OPENPLANETDATA_SHARED_DIR}/planet-latest.coastline.gpkg"
SHARED_PLANET_OSM_GOL_PATH = f"{OPENPLANETDATA_SHARED_DIR}/planet-latest.osm.gol"
SHARED_PLANET_OSM_PBF_PATH = f"{OPENPLANETDATA_SHARED_DIR}/planet-latest.osm.pbf"