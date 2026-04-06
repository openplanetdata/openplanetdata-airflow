"""
OpenPlanetData Airflow - Shared constants and defaults for Airflow workflows.
"""

from openplanetdata.airflow.defaults import (
    DOCKER_MOUNT,
    OPENPLANETDATA_IMAGE,
    R2_BUCKET,
    R2INDEX_CONNECTION_ID,
)

__all__ = [
    "DOCKER_MOUNT",
    "OPENPLANETDATA_IMAGE",
    "R2_BUCKET",
    "R2INDEX_CONNECTION_ID",
]
