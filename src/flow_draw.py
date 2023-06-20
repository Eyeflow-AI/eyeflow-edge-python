"""
SiliconLife Eyeflow
Class to draw flow annotations in a image

Author: Alex Sobral de Freitas
"""

import copy
import traceback
import importlib

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from eyeflow_sdk.log_obj import log
#----------------------------------------------------------------------------------------------------------------------------------


class FlowDraw(object):
    def __init__(self, out_size, rgbd_video=False):
        self._out_size = out_size
        self._rgbd_video = rgbd_video

        out_img = Image.new('RGB', out_size)
        draw_obj = ImageDraw.Draw(out_img)
        end_size = int(min(self._out_size[0], self._out_size[1]) * 0.02)
        display_txt = 'Test TEXT'
        ini_size = 8

        try:
            try:
                font_name = 'DejaVuSansMono.ttf'
                self._draw_font = ImageFont.truetype(font_name, ini_size)
                self._txt_size = draw_obj.textsize(display_txt, font=self._draw_font)
                while self._txt_size[1] < end_size:
                    ini_size += 1
                    self._draw_font = ImageFont.truetype(font_name, ini_size)
                    self._txt_size = draw_obj.textsize(display_txt, font=self._draw_font)
            except:
                font_name = 'arial.ttf'
                self._draw_font = ImageFont.truetype(font_name, ini_size)
                self._txt_size = draw_obj.textsize(display_txt, font=self._draw_font)
                while self._txt_size[1] < end_size:
                    ini_size += 1
                    self._draw_font = ImageFont.truetype(font_name, ini_size)
                    self._txt_size = draw_obj.textsize(display_txt, font=self._draw_font)
        except:
            font_name = 'Keyboard.ttf'
            self._draw_font = ImageFont.truetype(font_name, ini_size)
            self._txt_size = draw_obj.textsize(display_txt, font=self._draw_font)
            while self._txt_size[1] < end_size:
                ini_size += 1
                self._draw_font = ImageFont.truetype(font_name, ini_size)
                self._txt_size = draw_obj.textsize(display_txt, font=self._draw_font)


    def draw_single_frame(self, draw_obj, offset_min, prediction, image):
        if "component_id" not in prediction or "component_name" not in prediction:
            log.warning(f"Incomplete data in prediction: {prediction}. Lacks component_id or component_name")
            return

        prediction = copy.deepcopy(prediction)
        comp_lib = importlib.import_module(f'{prediction["component_id"]}.{prediction["component_name"]}')

        if prediction.get("type") in ["cutter", "ocr"]:
            flag_draw_box = False
            for out in prediction["outputs"]:
                for det in prediction["outputs"][out]:
                    if "bbox" in det:
                        det["bbox"]["x_min"] = int(det["bbox"]["x_min"] * self._img_scale)
                        det["bbox"]["y_min"] = int(det["bbox"]["y_min"] * self._img_scale)
                        det["bbox"]["x_max"] = int(det["bbox"]["x_max"] * self._img_scale)
                        det["bbox"]["y_max"] = int(det["bbox"]["y_max"] * self._img_scale)
                        flag_draw_box = True

                        x_min = int(det["bbox"]["x_min"])
                        y_min = int(det["bbox"]["y_min"])

                    if "bounds" in det:
                        points = []
                        for point in det["bounds"]:
                            points.append([point[0] * self._img_scale, point[1] * self._img_scale])
                        det["bounds"] = points
                        flag_draw_box = True

                    for key in det.keys():
                        if key.startswith("component_"):
                            self.draw_single_frame(
                                draw_obj,
                                (x_min, y_min),
                                det[key],
                                image
                            )

            if flag_draw_box:
                comp_lib.Component.draw_image(draw_obj, self._draw_font, offset_min, prediction, image)

        else:
            if hasattr(comp_lib.Component, "draw_image"):
                comp_lib.Component.draw_image(
                    draw_obj,
                    self._draw_font,
                    offset_min,
                    prediction,
                    image
                )


    def draw_frames(self, inputs, preserve_resolution=False):
        try:
            outputs = []
            for fr in inputs:
                if self._rgbd_video:
                    img = fr["input_image"][:, :, 0:3].astype(np.uint8)
                    frame_img = Image.fromarray(img)
                else:
                    frame_img = Image.fromarray(fr["input_image"])
                    if not preserve_resolution:
                        self._img_scale = min(self._out_size[0] / frame_img.size[0], self._out_size[1] / frame_img.size[1])
                        out_size = (int(frame_img.size[0] * self._img_scale), int(frame_img.size[1] * self._img_scale))
                        frame_img = frame_img.resize(out_size, Image.ANTIALIAS)
                    else:
                        self._img_scale = 1

                draw_obj = ImageDraw.Draw(frame_img)
                display_txt = fr["output_data"]["camera_name"] + " - " + str(fr["frame_data"]["frame"])
                draw_obj.text((11, 11), display_txt, (0, 0, 0), font=self._draw_font)
                draw_obj.text((10, 10), display_txt, (255, 255, 255), font=self._draw_font)

                for key in fr["frame_data"].keys():
                    if key.startswith("component_"):
                        self.draw_single_frame(
                            draw_obj,
                            (0, 0),
                            fr["frame_data"][key],
                            frame_img
                        )

                outputs.append(frame_img)

            return outputs

        except Exception as excp:
            log.error('Fail drawing frame')
            log.error('Exception {}'.format(excp))
            log.error(traceback.format_exc())
#----------------------------------------------------------------------------------------------------------------------------------
