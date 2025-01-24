FROM ubuntu:20.04

ENV HOME=/home/zoomrec \
    TZ=Europe/Moscow \
    TERM=xfce4-terminal \
    START_DIR=/start \
    DEBIAN_FRONTEND=noninteractive \
    VNC_RESOLUTION=1024x576 \
    VNC_COL_DEPTH=24 \
    VNC_PW=zoomrec \
    VNC_PORT=5901 \
    DISPLAY=:1 \
    QT_PLUGIN_PATH=/opt/zoom/Qt/plugins \
    LD_LIBRARY_PATH=/opt/zoom/Qt/lib:/opt/zoom \
    QT_QPA_PLATFORM_PLUGIN_PATH=/opt/zoom/Qt/plugins/platforms \
    XDG_SESSION_TYPE=x11 \
    XDG_CURRENT_DESKTOP=XFCE \
    XVFB_WHD="1920x1080x24" \
    QT_X11_NO_MITSHM=1 \
    QT_GRAPHICSSYSTEM="native" \
    PYTHONPATH=/home/zoomrec

# Add user
RUN useradd -ms /bin/bash zoomrec -d ${HOME}
WORKDIR ${HOME}

# Copy requirements first to leverage Docker cache
COPY requirements.txt ${HOME}/requirements.txt

# Install some tools
RUN apt-get update && \
    apt-get install --no-install-recommends -y \
        apt \
        apt-utils \
        ca-certificates \
        publicsuffix \
        libapt-pkg6.0 \
        libpsl5 \
        libssl1.1 \
        libnss3 \
        openssl \
        wget \
        locales \
        bzip2 \
        tzdata && \
# Generate locales for en_US.UTF-8
    locale-gen en_US.UTF-8 && \
# Install tigervnc
    wget -q -O tigervnc-1.10.0.x86_64.tar.gz https://sourceforge.net/projects/tigervnc/files/stable/1.10.0/tigervnc-1.10.0.x86_64.tar.gz && \
    tar xz -f tigervnc-1.10.0.x86_64.tar.gz --strip 1 -C / && \
    rm -rf tigervnc-1.10.0.x86_64.tar.gz && \
# Install xfce ui
    apt-get install --no-install-recommends -y \
        supervisor \
        xfce4 \
        xfce4-goodies \
        xfce4-pulseaudio-plugin \
        xfce4-terminal \
        xubuntu-icon-theme && \
# Install pulseaudio
    apt-get install --no-install-recommends -y \
        pulseaudio \
        pavucontrol && \
# Install necessary packages
    apt-get install --no-install-recommends -y \
        ibus \
        dbus-user-session \
        dbus-x11 \
        dbus \
        at-spi2-core \
        xauth \
        x11-xserver-utils \
        libxkbcommon-x11-0 && \
# Install Zoom dependencies
    apt-get install --no-install-recommends -y \
        libxcb-xinerama0 \
        libglib2.0-0 \
        libxcb-shape0 \
        libxcb-shm0 \
        libxcb-xfixes0 \
        libxcb-randr0 \
        libxcb-image0 \
        libfontconfig1 \
        libgl1-mesa-glx \
        libegl1-mesa \
        libxi6 \
        libsm6 \
        libxrender1 \
        libpulse0 \
        libxcomposite1 \
        libxslt1.1 \
        libsqlite3-0 \
        libxcb-keysyms1 \
        libxcb-xtest0 \
        libxcb-cursor0 \
        libxcb-icccm4 \
        libatomic1 \
        libqt5gui5 \
        libqt5widgets5 \
        libqt5core5a \
        libqt5dbus5 \
        libqt5network5 \
        libxcb-util1 \
        libxcb-xkb1 \
        xdg-desktop-portal \
        xdg-desktop-portal-gtk \
        libxcb-xinput0 \
        libxcb-xfixes0 \
        libxcb-render-util0 \
        libxcb-render0 \
        libxcb-present0 \
        libxcb-sync1 && \
# Install Zoom
    wget -q -O zoom_amd64.deb https://cdn.zoom.us/prod/6.3.6.6315/zoom_amd64.deb && \
    dpkg -i zoom_amd64.deb && \
    apt-get -f install -y && \
    rm -rf zoom_amd64.deb && \
# Install FFmpeg
    apt-get install --no-install-recommends -y \
        ffmpeg \
        libavcodec-extra && \
# Install Python dependencies for script
    apt-get install --no-install-recommends -y \
        python3 \
        python3-pip \
        python3-tk \
        python3-dev \
        python3-setuptools \
        scrot \
        gnome-screenshot \
        python3-pyqt5 \
        libqt5x11extras5 \
        libxcb-xinerama0-dev \
        libxcb-icccm4-dev \
        libxcb-image0-dev \
        libxcb-keysyms1-dev \
        libxcb-randr0-dev && \
    pip3 install --upgrade --no-cache-dir -r ${HOME}/requirements.txt && \
# Install VLC - optional
    apt-get install --no-install-recommends -y vlc && \
# Clean up
    apt-get autoremove --purge -y && \
    apt-get autoclean -y && \
    apt-get clean -y && \
    rm -rf /var/lib/apt/lists/*

# Allow access to pulseaudio
RUN adduser zoomrec pulse-access

USER zoomrec

# Add home resources
ADD res/home/ ${HOME}/

# Add startup scripts
ADD res/entrypoint.sh ${START_DIR}/entrypoint.sh
ADD res/xfce.sh ${START_DIR}/xfce.sh

# Create necessary directories
RUN mkdir -p ${HOME}/recordings ${HOME}/audio ${HOME}/img

# Copy source code
COPY src/ ${HOME}/src/
COPY main.py ${HOME}/

# Copy resources
COPY res/img/ ${HOME}/img/

# Set permissions
USER 0
RUN chmod a+x ${START_DIR}/entrypoint.sh && \
    chmod -R a+rw ${START_DIR} && \
    chown -R zoomrec:zoomrec ${HOME} && \
    find ${HOME}/ -name '*.sh' -exec chmod -v a+x {} + && \
    find ${HOME}/ -name '*.desktop' -exec chmod -v a+x {} + && \
    chmod +x ${HOME}/main.py

EXPOSE ${VNC_PORT}
USER zoomrec
CMD ${START_DIR}/entrypoint.sh
