"""
Shared default constants for OpenPlanetData Airflow workflows.
"""

ALERT_EMAIL = "airflow@openplanetdata.com"
DOCKER_MOUNT = {"source": "/data/airflow", "target": "/data", "type": "bind"}
OPENPLANETDATA_IMAGE = "openplanetdata/openplanetdata-airflow:latest"
OPENPLANETDATA_SHARED_DIR = "/data/openplanetdata/shared"
OPENPLANETDATA_WORK_DIR = "/data/openplanetdata"
R2INDEX_CONNECTION_ID = "r2index-openplanetdata-production"
R2_BUCKET = "openplanetdata"

SHARED_PLANET_OSM_PBF_PATH = f"{OPENPLANETDATA_SHARED_DIR}/planet-latest.osm.pbf"