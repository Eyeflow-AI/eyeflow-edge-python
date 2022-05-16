"""
SiliconLife Eyeflow
Function to run a flow at edge

Author: Alex Sobral de Freitas
"""

import os
import traceback
import sys
import argparse
from eyeflow_sdk import edge_client
# import edge_client

import tensorflow as tf

os.environ["CONF_PATH"] = os.path.dirname(__file__)

from eyeflow_sdk.log_obj import log

import flow_run
import utils
import json
#----------------------------------------------------------------------------------------------------------------------------------

def parse_args(args):
    """ Parse the arguments.
    """
    parser = argparse.ArgumentParser(description='Process a flow.')
    parser.add_argument('--monitor', help='Show image of detection real-time.', action='store_true')
    parser.add_argument('--video', help='Record image of detection in a video.', action='store_true')
    parser.add_argument('--save_img', help='Save image of detections to a folder.', type=str)

    return parser.parse_args(args)
#----------------------------------------------------------------------------------------------------------------------------------

def load_edge_data_json_file(json_path):
    log.info(f'Loading Json: {json_path}')
    with open(json_path, 'r') as json_file:
        return json.load(json_file)
#----------------------------------------------------------------------------------------------------------------------------------

def main(args=None):
    # parse arguments
    if args is None:
        args = sys.argv[1:]

    args = parse_args(args)

    os.environ['TF_CUDNN_USE_AUTOTUNE'] = "1"
    # CUDNN_LOGINFO_DBG=1;
    # CUDNN_LOGDEST_DBG=stdout

    physical_devices = tf.config.experimental.list_physical_devices('GPU')
    assert len(physical_devices) > 0, "Not enough GPU hardware devices available"
    config = tf.config.experimental.set_memory_growth(physical_devices[0], True)

    app_info, app_token = utils.get_license()
    log.info(f'Edge ID: {app_info["edge_id"]} - System ID: {app_info.get("device_sn")}')
    utils.check_license(app_info)

    try:
        edge_data = edge_client.get_edge_data(app_token)
        if not edge_data:
            json_path = f'/opt/eyeflow/src/edge_data.json'
            edge_data = load_edge_data_json_file(json_path)
            if not edge_data
                raise Exception("Fail getting edge_data")

        log.info(edge_data)
        flow_id = edge_data["flow_id"]

        out_monitor = []
        if args.monitor:
            mon = flow_run.MonitorShow(flow_id)
            out_monitor.append(mon)

        if args.video:
            vid = flow_run.VideoSave(flow_id)
            out_monitor.append(vid)

        if args.save_img:
            sav = flow_run.ImageSave(flow_id, args.save_img)
            out_monitor.append(sav)

        log.info(f"Runnig flow at edge - Flow ID: {flow_id}")

        flow_data = edge_client.get_flow(app_token, flow_id)
        utils.prepare_models(app_token, flow_data)
        utils.get_flow_components(app_token, flow_data)

        flow_obj = flow_run.FlowRun(flow_id, flow_data, device_info=app_info["edge_id"])
        flow_obj.process_flow(img_output=out_monitor, out_frame=(1530, 1020))

        utils.upload_flow_extracts(app_token, flow_data)

    except Exception as expt:
        log.error(f'Fail processing flow')
        log.error(traceback.format_exc())
        return
#----------------------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    main()
