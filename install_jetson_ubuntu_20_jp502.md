## Install JetPack on your Jetson device.
## Download SD Card Image for your Jetson model at https://developer.nvidia.com/embedded/downloads
Follow the install instructions until boot your board and get the graphical UI


## Set max performance/power
## For Jetson Nano
```
sudo /usr/sbin/nvpmodel -m 0
```
## For Jetson Xavier NX
```
sudo /usr/sbin/nvpmodel -m 2
```


## Install system packages
```
sudo apt-get update -y && sudo apt-get upgrade -y
sudo apt install -y \
    gcc \
    g++ \
    gfortran \
    build-essential \
    software-properties-common \
    python3 \
    python3-pip \
    python3-dev \
    python3-setuptools \
    libhdf5-serial-dev \
    libblas3 \
    libblas-dev \
    liblapack3 \
    liblapack-dev \
    libatlas-base-dev \
    libjpeg8-dev \
    libtiff5-dev \
    zlib1g-dev \
    freetype* \
    libtiff-dev \
    libjpeg-dev \
    libpng-dev \
    libsm6 \
    libxext6 \
    libxrender-dev \
    fonts-dejavu-core

sudo apt-get remove x264 libx264-dev \
	&& sudo apt-get upgrade -y \
	&& sudo apt-get install -y --no-install-recommends \
      libgtk2.0-dev libeigen3-dev libtheora-dev libvorbis-dev libxvidcore-dev libx264-dev sphinx-common libfaac-dev libopencore-amrnb-dev libopencore-amrwb-dev \
      libopenexr-dev libgstreamer1.0-0 libgstreamer-plugins-base1.0-dev libavutil-dev libavfilter-dev \
      libtbb2 libtbb-dev libavcodec-dev libavformat-dev libswscale-dev \
      libeigen3-dev ffmpeg libxine2-dev libv4l-dev \
      gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly gstreamer1.0-libav gstreamer1.0-tools \
      libxvidcore-dev libx264-dev libmp3lame-dev x264 v4l-utils
```


## Install Python packages
```
sudo -H python3 -m pip install --upgrade pip
sudo -H python3 -m pip install --upgrade --no-cache-dir --trusted-host pypi.python.org \
    wheel \
    setuptools \
    six \
    numpy==1.23.1 \
    pybind11 \
    Cython \
    testresources \
    protobuf


sudo -H python3 -m pip install --no-cache-dir --upgrade --trusted-host pypi.python.org \
    DateTime \
    decorator \
    tables \
    h5py \
    scipy \
    scikit-learn \
    pika \
    arrow \
    psutil \
    pynvml \
    Pillow \
    pymongo \
    opencv_python \
    tqdm \
    keras_resnet \
    arrow \
    psutil \
    pynvml \
    azure-storage-blob \
    eyeflow_sdk
```

## Install TensorFlow using the pip3 command. This command will install TensorFlow from NVidia.
```
sudo pip3 install --pre --extra-index-url https://developer.download.nvidia.com/compute/redist/jp/v502 tensorflow==2.9.1
```

## Create eyeflow directory
```
sudo mkdir -p /opt/eyeflow/data
sudo mkdir -p /opt/eyeflow/src
sudo mkdir -p /opt/eyeflow/log

sudo setfacl -dm u::rwx,g::rwx,o::rx /opt/eyeflow
sudo chmod g+rwxs /opt/eyeflow
sudo chown -R :users /opt/eyeflow
```

## Copy files to eyeflow directory
```
cd /opt
sudo git clone https://github.com/Eyeflow-AI/eyeflow-edge-python.git
sudo rsync -zvrh /opt/eyeflow-edge-python/* /opt/eyeflow/
cd /opt/eyeflow
sudo chmod +x edge_run.sh
```

## If will use a USB camera it need to set USB to max speed
```
echo 1000 > /sys/module/usbcore/parameters/usbfs_memory_mb
```
