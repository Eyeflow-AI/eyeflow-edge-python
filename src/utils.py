from codecs import encode
import os
import traceback
import sys
import platform
import importlib
import socket
import uuid
# import json
import jwt
# from bson import ObjectId

from eyeflow_sdk.log_obj import log, CONFIG
from eyeflow_sdk import jetson_utils
from eyeflow_sdk import edge_client
#----------------------------------------------------------------------------------------------------------------------------------


def load_model_component(model_component_id, model_component_name):
    sys.path.insert(0, CONFIG["file-service"]["model-components"]["local_folder"])

    try:
        log.info(f"Load component: {model_component_name}-{model_component_id}")
        comp_lib = importlib.import_module(f'{model_component_id}.{model_component_name}')
        return comp_lib
    except Exception as expt:
        log.error(f'Fail loading component {model_component_name}-{model_component_id} - {expt}')
        log.error(traceback.format_exc())
        raise Exception(f'Fail loading component {model_component_name}-{model_component_id}')
#----------------------------------------------------------------------------------------------------------------------------------


def prepare_models(app_token, flow_data):
    """
    Prepare datasets for processing flow
    """

    log.info(f"Prepare datasets for processing video")

    datasets_downloaded = []
    components_downloaded = []
    for comp in flow_data["nodes"]:
        if "dataset_id" in comp["options"]:
            dataset_id = comp["options"]["dataset_id"]
            if dataset_id not in datasets_downloaded:
                datasets_downloaded.append(dataset_id)
                model_folder = CONFIG["file-service"]["model"]["local_folder"]
                edge_client.get_model(app_token, dataset_id, model_folder=model_folder)
                model_file = os.path.join(model_folder, dataset_id, dataset_id + ".json")
                if not os.path.isfile(model_file):
                    log.info(f'Model for dataset {dataset_id} not found. Generating.')
                    dataset = edge_client.get_dataset(app_token, dataset_id)
                    if not dataset:
                        log.error(f'Fail loading dataset {dataset_id}')
                        raise Exception(f'Fail loading dataset {dataset_id}')

                    if "dnn_parms" in dataset["dataset_parms"]:
                        dnn_parms = dataset["dataset_parms"]["dnn_parms"]
                    elif "network_parms" in dataset["dataset_parms"] and "dnn_parms" in dataset["dataset_parms"]["network_parms"]:
                        dnn_parms = dataset["dataset_parms"]["network_parms"]["dnn_parms"]
                    else:
                        raise Exception(f'dnn_parms not found in dataset_parms: {dataset["dataset_parms"]}')

                    component_name = dnn_parms.get("component_name", dnn_parms["component"])
                    component_id = dnn_parms.get("component_id")
                    if not component_id:
                        if component_name == "objdet_af":
                            component_id = "6143a1faef5cc63fd4c177b1"
                        elif component_name == "objdet":
                            component_id = "6143a1edef5cc63fd4c177b0"
                        elif component_name == "class_cnn":
                            component_id = "614388073a692cccdab0e69b"
                        elif component_name == "obj_location":
                            component_id = "6178516681cbe716153175b0"

                    if component_id not in components_downloaded:
                        components_downloaded.append(component_id)
                        if not edge_client.get_model_component(
                            app_token,
                            model_component_id=component_id,
                            model_component_folder=CONFIG["file-service"]["model-components"]["local_folder"]
                        ):
                            log.error(f'Fail get_model_component {component_id}')
                            raise Exception(f'Fail get_model_component {component_id}')

                    comp_lib = load_model_component(component_id, component_name)
                    dnn_component = comp_lib.Component(dataset_id, dataset["dataset_parms"])
                    dnn_component.set_model(train=False)
                    dnn_component.export_model(model_path=os.path.join(model_folder, dataset_id))
#----------------------------------------------------------------------------------------------------------------------------------


def get_flow_components(app_token, flow_data):
    """
    Download components for processing video
    """

    log.info(f"Download components for processing video")

    flow_component_folder = CONFIG["file-service"]["flow-components"]["local_folder"]

    components_downloaded = []
    for comp in flow_data["nodes"]:
        component_id = comp["component_id"]
        if component_id not in components_downloaded:
            if not edge_client.get_flow_component(
                app_token,
                flow_component_id=component_id,
                flow_component_folder=flow_component_folder
            ):
                log.error(f'Fail loading flow_component_id {component_id}')
                raise Exception(f'Fail loading flow_component_id {component_id}')

            components_downloaded.append(component_id)

    sys.path.insert(0, flow_component_folder)
#----------------------------------------------------------------------------------------------------------------------------------


def upload_flow_extracts(app_token, flow_data, max_examples=400):
    """
    Upload extracts to datasets after processing video
    """

    log.info(f"Upload extracts for flow")

    datasets_uploaded = []
    for comp in flow_data["nodes"]:
        if "dataset_id" in comp["options"] and comp["options"]["dataset_id"] not in datasets_uploaded:
            dataset_id = comp["options"]["dataset_id"]
            datasets_uploaded.append(dataset_id)
            if not edge_client.upload_extract(
                app_token,
                dataset_id,
                extract_folder=CONFIG["file-service"]["extract"]["local_folder"],
                max_files=max_examples,
                thumb_size=128
            ):
                log.error(f'Fail uploading extract {dataset_id}')
#----------------------------------------------------------------------------------------------------------------------------------


def get_license(filename="edge.license"):
    # read app_token
    license_file = os.path.join(os.path.dirname(__file__), filename)
    if not os.path.isfile(license_file):
        log.error(f'Error: license_file not found {license_file}')
        raise Exception(f'Error: license_file not found {license_file}')

    with open(license_file, 'r') as fp:
        app_token = fp.read()

    key_file = os.path.join(os.path.dirname(__file__), "edge-key.pub")
    if not os.path.isfile(key_file):
        log.error(f'Error: token pub key not found {key_file}')
        raise Exception(f'Error: token pub key not found {key_file}')

    with open(key_file) as fp:
        public_key = fp.read()

    app_info = jwt.decode(app_token, public_key, algorithms=['RS256'])
    return app_info, app_token
#----------------------------------------------------------------------------------------------------------------------------------


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP
#----------------------------------------------------------------------------------------------------------------------------------


def get_device_sn():
    try:
        filename = "/sys/class/dmi/id/product_uuid"
        if os.path.isfile(filename):
            with open(filename, 'r') as fp:
                device_id = fp.readline()

            return device_id.rstrip()
    except:
        return None
#----------------------------------------------------------------------------------------------------------------------------------


def get_device_info():
    plat_info = platform.platform().split('-')
    if plat_info[0] != "Linux":
        raise Exception(f"Invalid platform: {plat_info[0]}")

    if "aarch64" in plat_info:
        idx = plat_info.index("aarch64")
        device_arch = f"{plat_info[idx - 1]}-{plat_info[idx]}"
        device_sn = jetson_utils.get_jetson_module_sn()
    elif "x86_64" in plat_info:
        idx = plat_info.index("x86_64")
        device_arch = f"{plat_info[idx - 1]}-{plat_info[idx]}"
        device_sn = get_device_sn()
    # 'WSL2-x86_64'
    else:
        raise Exception(f"Invalid device_architecture: {'-'.join(plat_info)}")

    sys_info = {
        "hostname": socket.gethostname(),
        "ip": get_ip(),
        "device_sn": device_sn,
        "device_architecture": device_arch
    }

    node_id = uuid.getnode()
    if node_id == uuid.getnode():
        sys_info["node_id"] = node_id

    return sys_info
#----------------------------------------------------------------------------------------------------------------------------------


def check_license(license_info):
    device_info = get_device_info()
    print(device_info)
    # if license_info.get("hostname"):
    #     if device_info["hostname"] != license_info["hostname"]:
    #         raise Exception("Invalid license for device")

    # if license_info.get("ip"):
    #     if device_info["ip"] != license_info["ip"]:
    #         raise Exception("Invalid license for device")

    # if license_info.get("device_architecture"):
    #     if device_info["device_architecture"] != license_info["device_architecture"]:
    #         raise Exception("Invalid license for device")

    if license_info.get("device_sn"):
        if device_info["device_sn"] != license_info["device_sn"]:
            if device_info["device_architecture"] == "generic-x86_64" and not device_info["device_sn"]:
                log.warning("Must run as root")
            else:
                raise Exception("Invalid license for device")

    # if license_info.get("node_id"):
    #     if device_info["node_id"] != license_info["node_id"]:
    #         log.warning("Invalid node_id")
            # raise Exception("Invalid license for device")
#----------------------------------------------------------------------------------------------------------------------------------
