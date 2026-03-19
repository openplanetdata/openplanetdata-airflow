# openplanetdata-airflow

Shared Airflow infrastructure for [OpenPlanetData](https://github.com/openplanetdata) workflows. Provides custom operators, shared constants, and static geospatial data for processing OpenStreetMap data pipelines.

## Installation

```bash
pip install openplanetdata-airflow
```

## Operators

### Ogr2OgrOperator

Runs [ogr2ogr](https://gdal.org/en/stable/programs/ogr2ogr.html) inside a GDAL Docker container. Supports Airflow template rendering and dynamic task mapping with `expand()`.

```python
from openplanetdata.airflow.operators.ogr2ogr import Ogr2OgrOperator

convert = Ogr2OgrOperator(
    task_id="convert",
    args=["-f", "GPKG", "output.gpkg", "input.geojson"],
)
```

### GolOperator

Runs [gol](https://docs.geodesk.com/gol) commands inside the OpenPlanetData Docker container, with optional output file redirection.

```python
from openplanetdata.airflow.operators.gol import GolOperator

query = GolOperator(
    task_id="query",
    args=["query", "planet.gol", "a[boundary=administrative]"],
    output_file="/data/output.geojson",
)
```

## Shared defaults

The `openplanetdata.airflow.defaults` module provides shared constants:

| Constant | Description |
|---|---|
| `DOCKER_MOUNT` | Bind mount configuration for `/data` |
| `GDAL_IMAGE` | GDAL Docker image reference |
| `OPENPLANETDATA_IMAGE` | OpenPlanetData worker Docker image |
| `OPENPLANETDATA_WORK_DIR` | Working directory path |
| `OPENPLANETDATA_SHARED_DIR` | Shared data directory path |
| `EMAIL_ALERT_RECIPIENTS` | Alert email recipients |
| `R2_BUCKET` | Cloudflare R2 bucket name |
| `R2INDEX_CONNECTION_ID` | Airflow connection ID for R2 |

## Static data

- `openplanetdata.airflow.data.continents` — list of 7 continents with names and slugs
- `openplanetdata.airflow.data.countries` — 250 countries and territories with ISO 3166-1 alpha-2 codes and coastline flags

## Docker image

The `docker/` directory contains a multi-stage Dockerfile that builds an Airflow worker image with geospatial tools pre-installed:

- [GOL](https://github.com/clarisma/gol) (Geodesk) for OSM boundary queries
- [osmcoastline](https://osmcode.org/osmcoastline/) for coastline extraction
- GDAL/OGR for format conversions
- [pyosmium](https://osmcode.org/pyosmium/) for OSM data updates
- aria2 for fast downloads

## License

MIT
