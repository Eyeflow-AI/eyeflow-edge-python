## Install WSL2 on your Windows.
https://docs.microsoft.com/windows/wsl/install

## Install Ubuntu 20.04
wsl.exe --install -d Ubuntu-20.04

## Download and install NVidia Cuda Driver on WSL2
https://developer.nvidia.com/cuda/wsl

## Install system packages
```
sudo apt-get update -y && apt-get upgrade -y
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
```

## Install cuda on wsl
```
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/cuda-keyring_1.0-1_all.deb
sudo dpkg -i cuda-keyring_1.0-1_all.deb
sudo apt update
sudo apt -y install cuda-toolkit-11-2
sudo apt -y install libcudnn8 libcudnn8-dev
```

## Install Python packages
```
sudo -H pip3 install --upgrade pip

sudo -H python3 -m pip install --upgrade --no-cache-dir --trusted-host pypi.python.org \
    wheel \
    setuptools \
    six \
    numpy==1.18.5 \
    pybind11 \
    Cython \
    testresources \
    pkgconfig \
    protobuf

sudo -H python3 -m pip install --no-cache-dir --upgrade --trusted-host pypi.python.org \
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
    eyeflow_sdk

sudo -H python3 -m pip install --no-cache-dir --upgrade --trusted-host pypi.python.org tensorflow==2.2.1
```

## Create eyeflow directory
```
sudo mkdir /opt/eyeflow
sudo setfacl -dm u::rwx,g::rwx,o::rx /opt/eyeflow
sudo chmod g+rwxs /opt/eyeflow

sudo mkdir /opt/eyeflow/data
sudo mkdir /opt/eyeflow/src
sudo mkdir /opt/eyeflow/log

sudo chown -R :users /opt/eyeflow
```

## Copy files to eyeflow directory
```
sudo cp ./edge_run.sh /opt/eyeflow
sudo cp ./src/* /opt/eyeflow/src
```

## Generate device info for license
```
python3 /opt/eyeflow/src/request_license <edge-id> <env-id>
```
