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


## Install Python packages
```
sudo -H pip3 install --upgrade pip

sudo -H pip3 install --upgrade --no-cache-dir --trusted-host pypi.python.org \
    wheel \
    setuptools==49.6.0 \
    future==0.18.2 \
    six \
    numpy==1.19.4 \
    mock==3.0.5 \
    pybind11 \
    cython \
    testresources \
    pkgconfig \
    protobuf

sudo -H pip3 install --upgrade --no-cache-dir --no-deps --trusted-host pypi.python.org \
    keras_preprocessing==1.1.2 \
    keras_applications==1.0.8 \
    gast==0.4.0 \
    scikit_learn \
    Pillow \
    pymongo \
    pkgconfig \
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
    google_pasta \
    opt_einsum \
    termcolor

sudo env H5PY_SETUP_REQUIRES=0 pip3 install -U h5py==3.1.0

sudo -H pip3 install --upgrade --no-cache-dir --trusted-host pypi.python.org eyeflow_sdk
```

## Install TensorFlow using the pip3 command. This command will install TensorFlow from NVidia.
```
sudo pip3 install --pre --extra-index-url https://developer.download.nvidia.com/compute/redist/jp/v44 tensorflow==2.2.0
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


## If will use a USB camera it need to set USB to max speed
```
echo 1000 > /sys/module/usbcore/parameters/usbfs_memory_mb
```
