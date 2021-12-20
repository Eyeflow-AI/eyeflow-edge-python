FROM nvidia/cuda:10.2-cudnn7-runtime-ubuntu18.04
RUN apt-get update -y \
  && apt-get upgrade -y \
  && apt-get install -y --no-install-recommends \
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
    fonts-dejavu-core \
  && apt-get remove x264 libx264-dev \
  && apt-get upgrade -y \
  && apt-get install -y --no-install-recommends \
      libgtk2.0-dev libeigen3-dev libtheora-dev libvorbis-dev libxvidcore-dev libx264-dev sphinx-common libfaac-dev libopencore-amrnb-dev libopencore-amrwb-dev \
      libopenexr-dev libgstreamer1.0-0 libgstreamer-plugins-base1.0-dev libavutil-dev libavfilter-dev libavresample-dev \
      libtbb2 libtbb-dev libavcodec-dev libavformat-dev libswscale-dev libdc1394-22-dev \
      libeigen3-dev ffmpeg libxine2-dev libv4l-dev \
      gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly gstreamer1.0-libav gstreamer1.0-doc gstreamer1.0-tools \
      libxvidcore-dev libx264-dev qt5-default libmp3lame-dev x264 v4l-utils \
  && python3 -m pip install --upgrade pip \
  && python3 -m pip install --upgrade --no-cache-dir --trusted-host pypi.python.org \
    wheel \
    setuptools \
    six \
    numpy==1.18.5 \
    pybind11 \
    Cython \
    testresources \
    protobuf \
  && python3 -m pip install --no-cache-dir --upgrade --trusted-host pypi.python.org \
    DateTime \
    decorator \
    tables \
    h5py==2.10.0 \
    scipy==1.4.1 \
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
    PyJWT \
    eyeflow_sdk \
  && python3 -m pip install --no-cache-dir --upgrade --trusted-host pypi.python.org tensorflow==2.2.1 \
  && apt-get remove -y \
    gcc \
    g++ \
    gfortran \
    build-essential \
    software-properties-common \
    python3-dev \
    libblas-dev \
    liblapack-dev \
    libatlas-base-dev \
    libjpeg8-dev \
    libtiff5-dev \
    zlib1g-dev \
    libtiff-dev \
    libjpeg-dev \
    libpng-dev \
    libxrender-dev \
  && apt-get autoremove -y \
  && apt-get clean autoclean \
  && rm -rf /var/lib/{apt,dpkg,cache,log}/ \
  && rm -rf /usr/install/ \
  && rm -f /tmp/*

WORKDIR /usr/local/cuda/lib64
RUN ln -s libcudart.so.10.2.89 libcudart.so.10.1

RUN pip3 install --no-cache-dir --upgrade --trusted-host pypi.python.org eyeflow_sdk

RUN mkdir -p /opt/eyeflow/data
RUN mkdir -p /opt/eyeflow/data/flow
RUN mkdir -p /opt/eyeflow/data/models

ENV LD_LIBRARY_PATH=/usr/local/cuda/targets/x86_64-linux/lib/:/usr/local/cuda/extras/CUPTI/lib64:/usr/local/cuda/lib64${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}
ENV CUDA_HOME=/usr/local/cuda
ENV TF_FORCE_GPU_ALLOW_GROWTH='true'

# Create app directory
WORKDIR /opt/eyeflow/src
COPY ./src .

CMD [ "python3", "call_flow.py" ]
