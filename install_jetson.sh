# Install JetPack on your Jetson device.

# Set max clock
sudo nvpmodel -m 0
# sudo ~nvidia/jetson_clocks.sh
# Check clock
sudo nvpmodel -q --verbose
sudo ~nvidia/jetson_clocks.sh --show

echo "--Setup NTP--"
sudo echo "America/Sao_Paulo" | sudo tee /etc/timezone
sudo dpkg-reconfigure --frontend noninteractive tzdata
sudo timedatectl set-timezone America/New_York
date --set="2020-09-07 19:10:00"


# Install packages
sudo apt-get update -y
sudo apt-get upgrade -y
sudo apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    gfortran \
    build-essential \
    software-properties-common \
    hdf5-tools \
    libhdf5-dev \
    libhdf5-serial-dev \
    libblas3 \
    libblas-dev \
    liblapack3 \
    liblapack-dev \
    libatlas-base-dev \
    libjpeg8-dev \
    libtiff5-dev \
    zlib1g-dev \
    zip \
    freetype* \
    libtiff-dev \
    libjpeg-dev \
    libpng-dev \
    python3 \
    python3-pip \
    python3-dev \
    python3-setuptools


# Install Python packages
sudo -H pip3 install --upgrade pip

sudo -H pip3 install --upgrade --no-cache-dir --trusted-host pypi.python.org \
    wheel \
    setuptools \
    six \
    numpy \
    pybind11 \
    Cython \
    testresources \
    protobuf

sudo -H pip3 install --upgrade --no-cache-dir --trusted-host pypi.python.org \
    # scipy \
    joblib \
    threadpoolctl \
    scikit_learn \
    pika \
    pymongo \
    Pillow \
    pkgconfig \
    # h5py \
    Keras_Preprocessing \
    grpcio \
    tensorflow_estimator==2.2.0 \
    google_auth_oauthlib \
    google_auth \
    oauthlib \
    Werkzeug \
    requests \
    tensorboard_plugin_wit \
    absl_py \
    Markdown \
    requests_oauthlib \
    pyasn1_modules \
    pyasn1 \
    rsa \
    cachetools \
    importlib_metadata \
    zipp \
    tensorboard==2.2.2 \
    wrapt \
    astunparse \
    gast \
    google_pasta \
    opt_einsum \
    termcolor \
    azure-storage-blob

# 3. Installing TensorFlow
# Install TensorFlow using the pip3 command. This command will install the latest version of TensorFlow.
sudo pip3 install --pre --extra-index-url https://developer.download.nvidia.com/compute/redist/jp/v44 tensorflow==2.2.0

# If you want to install a specific version of TensorFlow, issue the following command:
# sudo pip3 install --extra-index-url https://developer.download.nvidia.com/compute/redist/jp/v42 tensorflow-gpu==$TF_VERSION+nv$NV_VERSION
# Where:
# TF_VERSION
# The released version of TensorFlow, for example, 1.12.0.
# NV_VERSION
# The monthly NVIDIA container version of TensorFlow, for example, 19.01.
# For example, to install TensorFlow 19.01, the command would look similar to the following:
# sudo pip3 install --extra-index-url https://developer.download.nvidia.com/compute/redist/jp/v42 tensorflow-gpu==1.

# open-cv
# sudo apt-get install -y --no-install-recommends \
#                     libgtk2.0-dev libeigen3-dev libtheora-dev libvorbis-dev libxvidcore-dev libx264-dev sphinx-common libfaac-dev libopencore-amrnb-dev libopencore-amrwb-dev \
#                     libopenexr-dev libgstreamer1.0-0 libgstreamer-plugins-base1.0-dev libavutil-dev libavfilter-dev libavresample-dev \
#                     libtbb2 libtbb-dev libavcodec-dev libavformat-dev libswscale-dev libdc1394-22-dev \
#                     libeigen3-dev ffmpeg libxine2-dev libv4l-dev \
#                     gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly gstreamer1.0-libav gstreamer1.0-doc gstreamer1.0-tools \
#                     libxvidcore-dev libx264-dev qt5-default libmp3lame-dev x264 v4l-utils

echo 1000 > /sys/module/usbcore/parameters/usbfs_memory_mb
