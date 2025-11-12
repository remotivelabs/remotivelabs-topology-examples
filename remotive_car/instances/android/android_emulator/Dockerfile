# Simple Ubuntu-based noVNC + x11vnc desktop
FROM eclipse-temurin:25_36-jdk

ARG TARGETPLATFORM
RUN [ "${TARGETPLATFORM}" = "linux/amd64" ] || \
  (echo "Unsupported platform ${TARGETPLATFORM}. Only linux/amd64 is supported" && exit 1)

ENV DEBIAN_FRONTEND=noninteractive \
  DISPLAY=:0 \
  SCREEN_RES=1920x1080x24

# Install packages: Xvfb (headless X), fluxbox (tiny WM), x11vnc, noVNC + websockify
RUN apt-get update && apt-get install -y --no-install-recommends \
  xvfb x11vnc fluxbox xterm novnc websockify android-tools-adb \
  ca-certificates wget curl unzip socat \
  libpulse-dev libnss3 libxshmfence-dev libdbus-glib-1-2 \
  && rm -rf /var/lib/apt/lists/*

ARG ARCH="x86_64"
ARG TARGET="android-automotive"
ARG API_LEVEL="33"
ARG BUILD_TOOLS="34.0.0"
ARG ANDROID_API_LEVEL="android-${API_LEVEL}"
ARG ANDROID_APIS="${TARGET};${ARCH}"
ARG EMULATOR_PACKAGE="system-images;${ANDROID_API_LEVEL};${ANDROID_APIS}"
ARG PLATFORM_VERSION="platforms;${ANDROID_API_LEVEL}"
ARG BUILD_TOOL="build-tools;${BUILD_TOOLS}"
ARG ANDROID_CMD="commandlinetools-linux-13114758_latest.zip"
ARG ANDROID_SDK_PACKAGES="${EMULATOR_PACKAGE} ${PLATFORM_VERSION} ${BUILD_TOOL} platform-tools emulator"

ENV ANDROID_SDK_ROOT=/opt/android
ENV PATH="$PATH:$ANDROID_SDK_ROOT/cmdline-tools/tools:$ANDROID_SDK_ROOT/cmdline-tools/tools/bin:$ANDROID_SDK_ROOT/emulator:$ANDROID_SDK_ROOT/tools/bin:$ANDROID_SDK_ROOT/platform-tools:$ANDROID_SDK_ROOT/build-tools/${BUILD_TOOLS}"

# Install android SDK and tools
RUN wget https://dl.google.com/android/repository/${ANDROID_CMD} -P /tmp && \
  unzip -d $ANDROID_SDK_ROOT /tmp/$ANDROID_CMD && \
  mkdir -p $ANDROID_SDK_ROOT/cmdline-tools/tools && cd $ANDROID_SDK_ROOT/cmdline-tools &&  mv NOTICE.txt source.properties bin lib tools/  && \
  cd $ANDROID_SDK_ROOT/cmdline-tools/tools && ls

RUN yes Y | sdkmanager --licenses
RUN yes Y | sdkmanager --verbose --no_https ${ANDROID_SDK_PACKAGES}

ARG EMULATOR_NAME="android-automotive"
ARG EMULATOR_DEVICE="automotive_1408p_landscape_with_google_apis"
ENV EMULATOR_NAME=$EMULATOR_NAME
ENV DEVICE_NAME=$EMULATOR_DEVICE

# Create android enulator image
RUN echo "no" | avdmanager --verbose create avd --force --name "${EMULATOR_NAME}" --device "${EMULATOR_DEVICE}" --package "${EMULATOR_PACKAGE}"

COPY com.google.android.apps.maps_*.apk /com.google.android.apps.maps.apk
RUN if [ ! -f /com.google.android.apps.maps.apk ]; then echo "Maps APK file is missing or not named com.google.android.apps.maps_*.apk" >&2; exit 1; fi
COPY start.sh /start.sh

EXPOSE 5037 6000 8080 33452

CMD ["/start.sh"]
