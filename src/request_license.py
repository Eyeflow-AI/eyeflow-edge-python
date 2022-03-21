import os
import sys
import time
import yaml
import json
import utils
import pprint
import requests
import argparse
from bson import ObjectId

CONFIG = None

os.environ["CONF_PATH"] = os.path.dirname(__file__)
with open(os.path.join(os.path.dirname(__file__), "eyeflow_conf.yaml"), "r") as ymlfile:
    CONFIG = yaml.safe_load(ymlfile)

#----------------------------------------------------------------------------------------------------------------------------------

def parse_args(args):
    """ Parse the arguments.
    """
    parser = argparse.ArgumentParser(prog='tokengen', description='Eyeflow Create Environment')
    parser.add_argument('edge_id', help='The ID of edge device', type=str)
    parser.add_argument('environment_id', help='The ID of client environment', type=str)
    parser.add_argument('--out_file', '-o', dest='out_file', help='The json file to save device info', type=str, action='store', default='license.json')

    return parser.parse_args(args)
#----------------------------------------------------------------------------------------------------------------------------------

def main(args=None):
    # parse arguments
    if args is None:
        args = sys.argv[1:]

    args = parse_args(args)

    device_info = utils.get_device_info()

    try:
        ObjectId(args.edge_id)
    except:
        print("ERROR: edge-id is not a valid ID")
        exit(1)

    try:
        ObjectId(args.environment_id)
    except:
        print("ERROR: environment-id is not a valid ID")
        exit(1)

    device_info["edge_id"] = args.edge_id
    device_info["environment_id"] = args.environment_id
    device_info["device_sn"] = device_info.get('device_sn') or None

    with open(args.out_file, 'w') as fp:
        json.dump(device_info, fp, default=str, ensure_ascii=False)

    # Start validation process
    validated = False
    response = requests.post(f"{CONFIG['ws']}/edge/activate/", data=device_info)
    if (response.json().get('payload')):        
        validation_code = response.json()['payload']['validation_code']
        print(f'Digite o código no front end {validation_code} para validar o device.')
        checking_info = {
            "edge_id": device_info["edge_id"],
            "environment_id": device_info["environment_id"],
            "validation_code": validation_code,
        }
        counter = 0
        while not validated:
            counter += 1
            print(f'{counter}ª Tentativa')
            get_response = requests.get(f"{CONFIG['ws']}/edge/check-validation/?edge_id={checking_info['edge_id']}&environment_id={checking_info['environment_id']}&validation_code={checking_info['validation_code']}")
            if (get_response.json().get('ok') == True):
                with open('edge.license', 'w') as _license:
                    _license.write(get_response.json()['info']['token'])
                with open('edge-key.pub', 'w') as _pub:
                    _pub.write(get_response.json()['info']['public_key'])
                validated = True
                print('Validated!')
            else:
                time.sleep(5)
    else:
        print(response.json()['error']['message'])
#----------------------------------------------------------------------------------------------------------------------------------

main()