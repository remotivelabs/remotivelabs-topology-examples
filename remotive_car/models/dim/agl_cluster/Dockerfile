# RemotiveCar instrument cluster as a RemotiveTopology ECU container (DIM).
#
# The container sits directly on the CAN buses of the DIM ECU. The cluster is a
# Qt/QML application derived from the AGL cluster demo dashboard that reads the
# buses over SocketCAN, decoding frames with code generated from the platform
# DBC files at build time. It renders through Qt's VNC platform plugin and noVNC
# serves the display as a web page on port 6080.
#
# Build context is the remotive_car directory (for the DBC files):
#   docker build -f models/dim/agl_cluster/Dockerfile .

ARG CANTOOLS_VERSION=44.1.0

# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
FROM debian:trixie-slim AS build
ARG CANTOOLS_VERSION

RUN apt-get update && apt-get install -y --no-install-recommends \
    g++ meson ninja-build pkg-config python3 python3-venv \
    qt6-base-dev qt6-base-private-dev qt6-declarative-dev \
    libwayland-dev \
    && rm -rf /var/lib/apt/lists/*

# cantools generates the CAN decoders from the DBC files
RUN python3 -m venv /opt/cantools && /opt/cantools/bin/pip install --no-cache-dir cantools==${CANTOOLS_VERSION}

COPY platform/databases/chassis_can.dbc platform/databases/body_can.dbc /src/dbc/
COPY models/dim/agl_cluster/app /src/app

RUN cd /src/app \
    && PATH=/opt/cantools/bin:$PATH meson setup build --prefix=/usr -Ddbc_dir=/src/dbc \
    && ninja -C build install

# ---------------------------------------------------------------------------
# Runtime
# ---------------------------------------------------------------------------
FROM debian:trixie-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    # Qt 6 / QML, rendered by the Qt VNC platform plugin
    qt6-qpa-plugins \
    qml6-module-qtqml qml6-module-qtqml-workerscript qml6-module-qtquick \
    qml6-module-qtquick-window qml6-module-qtquick-shapes \
    libwayland-client0 fonts-dejavu-core \
    # VNC in the browser
    novnc websockify \
    # tools
    can-utils \
    && rm -rf /var/lib/apt/lists/*

COPY --from=build /usr/bin/cluster-dashboard /usr/bin/cluster-dashboard
COPY models/dim/agl_cluster/entrypoint.sh /usr/bin/cluster
# The root of the noVNC port opens the cluster display directly
COPY models/dim/agl_cluster/index.html /usr/share/novnc/index.html

# The cluster is a 1920x720 frameless window; the VNC platform is a raster
# backend, so Qt Quick uses its software renderer.
ENV LANG=C.UTF-8 \
    QT_QPA_PLATFORM=vnc:size=1920x720 \
    QT_QUICK_BACKEND=software \
    CAN_CHASSIS=chassiscan0 \
    CAN_BODY=bodycan0

EXPOSE 6080

ENTRYPOINT ["/usr/bin/cluster"]
