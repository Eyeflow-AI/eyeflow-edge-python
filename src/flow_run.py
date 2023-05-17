"""
SiliconLife Eyeflow
Class to interpret and execute a Flow

Author: Alex Sobral de Freitas
"""

import os
import re
import sys
import traceback
import datetime
import math
from pathlib import Path
import copy
import importlib
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from bson import ObjectId

import numpy as np
import cv2
from eyeflow_sdk import img_utils
from eyeflow_sdk.log_obj import log, CONFIG
# ----------------------------------------------------------------------------------------------------------------------------------

class VideoSave():
    """
    Classe que recebe as imagens de um flow para salvar em um vídeo
    """

    def __init__(self, flow_id, out_frame=(1530, 1020)):
        video_path = Path(CONFIG["file-service"]["video"]["local_folder"])
        if not video_path.is_dir():
            video_path.mkdir(parents=True, exist_ok=True)

        self._flow_id = flow_id
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        datetime_now = datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S")
        intermediate_file = os.path.join(video_path, f"flow_run_proc-{datetime_now}.avi")
        self._out_video = cv2.VideoWriter(intermediate_file, fourcc, 5, out_frame, True)


    def __call__(self, frames):
        self._out_video.write(frames)


    def __del__(self):
        self._out_video.release()
# ----------------------------------------------------------------------------------------------------------------------------------

class MonitorShow():
    """
    Classe que recebe as imagens de um flow para mostrar em uma janela
    """

    def __init__(self, flow_id):
        self._flow_id = flow_id


    def __call__(self, frames):
        cv2.namedWindow('Detection', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('Detection', frames)


    def __del__(self):
        cv2.destroyAllWindows()
# ----------------------------------------------------------------------------------------------------------------------------------

class ImageSave():
    """
    Classe que recebe as imagens de um flow para salvar em uma pasta
    """

    def __init__(self, flow_id, save_path):
        save_path = Path(save_path)
        if not save_path.is_dir():
            save_path.mkdir(parents=True, exist_ok=True)

        self._flow_id = flow_id
        self._save_path = save_path


    def __call__(self, frames):
        try:
            img_file = os.path.join(self._save_path, f"{self._flow_id}.jpg")
            cv2.imwrite(img_file + "-tmp.jpg", np.array(frames))
            if os.path.isfile(img_file):
                os.remove(img_file)
            os.rename(img_file + "-tmp.jpg", img_file)
        except:
            pass

# ----------------------------------------------------------------------------------------------------------------------------------
images_data = {
    "frames": {},
    }
  

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):


    def do_GET(self):

        try:
            path = self.path
            query = ""
            if "?" in path:
                path, query = path.split("?")

            path = re.sub('/+', '/', path)
            if path.endswith("/"):
                path = path[:-1]

            camera_name_list = images_data["frames"].keys()

            if not self.path  or self.path == "/":

                self.send_json({"ok": True, "message": "Eyeflow Image Server"})


            elif self.path == "/cameras":
                response = {"ok": True, "cameras_list": []}
                for camera_name in images_data["frames"]:
                    response["cameras_list"].append({
                        "camera_name": camera_name,
                        "frame_time": images_data["frames"][camera_name]["frame_time"],
                        "url_path": f"/cameras/{camera_name}",
                    })

                self.send_json(response)


            elif path in [f"/cameras/{i}" for i in camera_name_list]:

                camera_name = path.replace('/cameras/', '')
                self.send_cv2_image(images_data["frames"][camera_name]["frame"])

            else:
                response = {"ok": False, "error": "Page not Found"}
                self.send_json(response, status=404)


        except Exception as e:

            response = {"ok": False, "error": str(e)}
            self.send_json(response, status=500)


    def send_json(self, data, status=200):

        response = bytes(json.dumps(data, default=str), "utf-8")
        self.protocol_version = 'HTTP/1.0'
        self.send_response(status)
        self.send_header("Content-type", 'application/json')
        self.send_header("Content-length", len(response))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(response)


    def send_cv2_image(self, cv2_image, status=200):

        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
        result, response = cv2.imencode('.jpg', cv2_image, encode_param)

        self.protocol_version = 'HTTP/1.0'
        self.send_response(status)
        self.send_header('Content-type', 'image/jpeg')
        self.send_header("Content-length", len(response))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(response)


    def send_pillow_image(self, pillow_image, status=200):

        self.send_cv2_image(
            cv2.cvtColor(np.array(pillow_image), cv2.COLOR_RGB2BGR),
            status
            )


class ImageServ():
    """
    Classe que recebe as imagens de um flow e as serve em uma porta em outra thread
    """
    
    def __init__(self, flow_id, host, port):

        self._flow_id = flow_id
        self._host = host
        self._port = port
        self._server = None
        self._server_thread = threading.Thread(target=self._start_server)
        self._server_thread.start()


    def _start_server(self):

        log.info(f"Starting Image Server on port {self._host}:{self._port}")
        self._server = HTTPServer((self._host, self._port), SimpleHTTPRequestHandler)
        self._server.serve_forever()


    def __call__(self, camera_name, image):

        try:
            images_data["frames"][camera_name] = {
                "frame_time": datetime.datetime.now(),
                "frame": image,
                }

        except:
            pass

# ----------------------------------------------------------------------------------------------------------------------------------

class SaveSplitImage():
    """
    Classe que salva as imagens das cameras separadamente
    """

    def __init__(self, dir):
        save_path = Path(dir)
        if not save_path.is_dir():
            save_path.mkdir(parents=True, exist_ok=True)

        self._save_path = save_path


    def __call__(self, image_name, image):
        try:
            img_file = os.path.join(self._save_path, image_name)
            cv2.imwrite(img_file + "-tmp.jpg", image)
            if os.path.isfile(img_file):
                os.remove(img_file)

            os.rename(img_file + "-tmp.jpg", img_file)
        except Exception as err:
            log.error(f'Failed to write image. Err: {err}')
            pass
# ----------------------------------------------------------------------------------------------------------------------------------

class FlowRun():
    """
    Classe que interpreta e executa um flow
    """

    def __init__(self, flow_id, flow_data, device_info, video_test=False, save_split_images=''):
        self._flow_id = flow_id
        self._flow_data = flow_data
        self._device_info = device_info
        self._save_split_images = save_split_images

        self._video_test = video_test
        self._device_info = None

        self._components = {}
        self._components["input"] = []
        self._components["input_agregation"] = []
        self.load_components()
        self.load_models()


    def load_components(self):
        comp_folder = CONFIG["file-service"]["flow-components"]["local_folder"]
        sys.path.insert(0, comp_folder)

        for comp in self._flow_data["nodes"]:
            if not (self._video_test and comp["options"]["phase"] == 'input'):
                try:
                    log.info(f'Load Component: {comp["component_name"]}')
                    comp_lib = importlib.import_module(f'{comp["component_id"]}.{comp["component_name"]}')
                    comp["object"] = comp_lib.Component(comp)
                except Exception as excp:
                    raise Exception(f'Component load fail: {comp["component_name"]} - {str(excp)}')

            if comp["options"]["phase"] == "input":
                self._components["input"].append(comp)

                if not self._video_test:
                    comp["object"].setup_device()

            if comp["options"]["phase"] == "input_agregation":
                self._components["input_agregation"].append(comp)

            self._components[comp["_id"]] = copy.copy(comp)


    def load_models(self):
        for comp_id in self._components:
            if comp_id not in ["input", "input_agregation"]:
                comp = self._components[comp_id]
                if comp["options"]["phase"] == "process":
                    if hasattr(comp["object"], "load_model"):
                        comp["object"].load_model()


    def process_frames(self, inputs):
        proc_stack = list()
        out_stack = list()

        if len(self._components["input_agregation"]):
            for comp in self._components["input_agregation"]:
                comp["object"].agregate_inputs(inputs)

        # Insert inputs in stack
        for inp in inputs:
            for dest_id in inp[1]:
                proc_stack.append((dest_id, inp[0]))

        # process phase
        while len(proc_stack) > 0:
            pack = proc_stack.pop(0)
            comp = self._components[pack[0]]
            try:
                res = comp["object"].process_inputs(pack[1])
            except Exception as excp:
                log.error(f'Fail processing inputs. Exception {excp}')
                log.error(traceback.format_exc())
                continue

            if not isinstance(res, dict):
                continue

            for out in res.keys():
                if out not in comp.get("outputs", {}):
                    log.warning(f'Output not in component: {out} - {comp["component_name"]} -  {comp}')
                    continue

                for dest_id in comp["outputs"][out]["nodes"]:
                    if not res[out]:
                        continue

                    # output = copy.deepcopy(res[out])
                    output = res[out]
                    if self._components[dest_id]["options"]["phase"] == "output" and len(output) > 0:
                        # concatenate/update outputs to a same destiny
                        for dest, out_comp in out_stack:
                            if dest == dest_id:
                                out_comp.extend(output)
                                out_comp.sort(key=lambda det: det["frame_data"]["frame"])
                                break
                        else:
                            out_stack.append((dest_id, output))
                    elif self._components[dest_id]["options"]["phase"] == "process" and len(output) > 0:
                        proc_stack.append((dest_id, output))
                    else:
                        raise Exception('Unknow phase: ' + self._components[dest_id]["phase"])

        # output phase
        while len(out_stack) > 0:
            pack = out_stack.pop(0)
            comp = self._components[pack[0]]
            try:
                res = comp["object"].process_inputs(pack[1])
            except Exception as excp:
                log.error(f'Fail processing inputs. Exception {excp}')
                log.error(traceback.format_exc())
                continue

            for out in res.keys():
                if out not in comp.get("outputs", {}):
                    log.warning(f'Output not in component: {out} - {comp["component_name"]} -  {comp}')
                    continue

                for dest_id in comp["outputs"][out]["nodes"]:
                    output = res[out]

                    if self._components[dest_id]["options"]["phase"] == "output" and len(output) > 0:
                        # concatenate/update outputs to a same destiny
                        updated = False
                        for dest, out_comp in out_stack:
                            if dest == dest_id:
                                updated = True
                                out_comp.extend(output)
                                out_comp = sorted(out_comp, key=lambda det: det["frame_data"]["frame"])
                                for new_fr in output:
                                    for fr in out_comp:
                                        if new_fr["frame_data"]["camera_name"] == fr["frame_data"]["camera_name"] and new_fr["frame_data"]["frame"] == fr["frame_data"]["frame"]:
                                            fr["frame_data"].update(new_fr["frame_data"])
                                            break
                                    else:
                                        out_comp.append(new_fr)

                        if not updated:
                            out_stack.append((dest_id, output))
                    else:
                        out_stack.append((dest_id, output))

        return [[p["output_data"] for p in cam[0]] for cam in inputs]


    def process_flow(self, img_output_single=[], image_output_multiple=[], out_frame=(1530, 1020)):
        key_press = 0

        if img_output_single or image_output_multiple:
            import flow_draw

            size_w = int(math.ceil(math.sqrt(len(self._components["input"]))))
            size_h = int(math.ceil(len(self._components["input"]) / size_w))
            out_size = (out_frame[0] // size_w, out_frame[1] // size_h)
            draw_obj = flow_draw.FlowDraw(out_size)

        key_event = False
        while True:
            try:
                frames_cams = []
                num_frames = 1
                for cam in self._components["input"]:
                    metadata = {
                        "device_info": self._device_info,
                        "flow_id": self._flow_id,
                        "modified_date": self._flow_data["modified_date"]
                    }

                    if self._flow_data.get("include_event_image", False):
                        metadata["event_image"] = ""
                        metadata["event_scale"] = self._flow_data.get("event_image_scale", 1.0)

                    if key_event:
                        metadata["key_event"] = True
                        key_event = False

                    cam_output = list(cam["outputs"].keys())[0]
                    frames_cams.append((cam["object"].get_frames(metadata, num_frames=num_frames), cam["outputs"][cam_output]["nodes"]))

                self.process_frames(frames_cams)

                if img_output_single or image_output_multiple:
                    frames_draw = []
                    for frames in frames_cams:
                        frame_draw = np.array(
                            draw_obj.draw_frames(frames[0])[0]
                            )
                        frames_draw.append(frame_draw)
                        for out_obj in image_output_multiple:
                            out_obj(frames[0][0]["frame_data"]["camera_name"], frame_draw)

                    if img_output_single:
                        merged_image = img_utils.merge_images(frames_draw).astype(np.uint8)
                        for out_obj in img_output_single:
                            out_obj(merged_image)

                    key_press = cv2.waitKey(1)
                    if key_press & 0xFF == ord('q'):
                        break
                    elif key_press & 0xFF == ord(' '):
                        key_event = True

                if key_press & 0xFF == ord('q'):
                    break

            except Exception as excp:
                log.error('Fail processing flow {}'.format(self._flow_id))
                log.error('Exception {}'.format(excp))
                log.error(traceback.format_exc())
                raise excp
# ----------------------------------------------------------------------------------------------------------------------------------
