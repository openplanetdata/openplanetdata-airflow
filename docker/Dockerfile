# OpenPlanetData Airflow worker image
# Based on official Apache Airflow image with geospatial tools:
# - osmcoastline: Coastline extraction from OSM PBF
# - gol: OSM boundary queries
# - GDAL/OGR: Geospatial format conversions (ogr2ogr, ogrinfo)
# - Python with pyproj: Area calculations and metadata

# Versions
ARG AIRFLOW_VERSION=3.1.7
ARG GOL_VERSION=2.2.3
ARG OSMCOASTLINE_VERSION=2.5.0
ARG PYTHON_VERSION=3.12

# =============================================================================
# Stage 1: Build GOL from source
# =============================================================================
FROM debian:bookworm-slim AS gol-builder

ARG GOL_VERSION

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    cmake \
    curl \
    g++-12 \
    git \
    libssl-dev \
    ninja-build \
    && rm -rf /var/lib/apt/lists/*

# Build GOL with GCC 12 and C++20 compatibility flags
RUN curl -fsSL "https://github.com/clarisma/geodesk-gol/archive/refs/tags/v${GOL_VERSION}.tar.gz" \
       -o /tmp/gol.tar.gz \
    && tar -xzf /tmp/gol.tar.gz -C /tmp \
    && cd /tmp/geodesk-gol-${GOL_VERSION} \
    && cmake -B build -G Ninja -DCMAKE_BUILD_TYPE=Release \
       -DCMAKE_CXX_COMPILER=/usr/bin/g++-12 \
       -DCMAKE_CXX_FLAGS="--param=destructive-interference-size=64 -include optional -Wno-error -Wno-deprecated-declarations -Wno-invalid-offsetof" \
       -DCMAKE_COMPILE_WARNING_AS_ERROR=OFF \
       -DGEODESK_GOL_VERSION=${GOL_VERSION} \
    && cmake --build build --target gol \
    && cp build/gol /usr/local/bin/gol

# =============================================================================
# Stage 2: Build osmcoastline from source
# =============================================================================
FROM debian:bookworm-slim AS osmcoastline-builder

ARG OSMCOASTLINE_VERSION

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    cmake \
    git \
    libgdal-dev \
    libgeos-dev \
    liblz4-dev \
    libosmium2-dev \
    libprotozero-dev \
    libspatialite-dev \
    libsqlite3-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

RUN git clone --branch v${OSMCOASTLINE_VERSION} --depth 1 \
        https://github.com/osmcode/osmcoastline.git /tmp/osmcoastline \
    && cmake -S /tmp/osmcoastline -B /tmp/osmcoastline/build \
        -DCMAKE_BUILD_TYPE=Release \
        -DWITH_LZ4=ON \
    && cmake --build /tmp/osmcoastline/build -j$(nproc) \
    && cmake --install /tmp/osmcoastline/build \
    && rm -rf /tmp/osmcoastline

# =============================================================================
# Stage 3: Final image based on Airflow slim
# =============================================================================
FROM apache/airflow:slim-${AIRFLOW_VERSION}-python${PYTHON_VERSION}

LABEL org.opencontainers.image.description="OpenPlanetData Airflow worker with geospatial tools"
LABEL org.opencontainers.image.source="https://github.com/openplanetdata/openplanetdata-airflow"

ARG AIRFLOW_VERSION

USER root

ENV DEBIAN_FRONTEND=noninteractive

# Install tools and runtime dependencies from Debian packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gdal-bin \
    jq \
    libgeos-c1v5 \
    liblz4-1 \
    libspatialite7 \
    sqlite3 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy GOL from builder
COPY --from=gol-builder /usr/local/bin/gol /usr/local/bin/gol

# Copy osmcoastline from builder
COPY --from=osmcoastline-builder /usr/local/bin/osmcoastline* /usr/local/bin/

USER airflow

# Install Python dependencies following Airflow best practices
COPY requirements.txt /
RUN pip install --no-cache-dir "apache-airflow==${AIRFLOW_VERSION}" -r /requirements.txt

# Verify installations
RUN gol --help \
    && ogr2ogr --version \
    && osmcoastline --version \
    && python -c "import pyproj; print(f'pyproj {pyproj.__version__}')"

# Environment variables
ENV GDAL_DATA=/usr/share/gdal
ENV OGR_GEOJSON_MAX_OBJ_SIZE=0
