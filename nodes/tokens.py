import json
import torch
from torch.functional import F
import numpy as np
from comfy.utils import ProgressBar, common_upscale
from contextlib import nullcontext
import comfy.model_management as mm
from tqdm import tqdm

class CountTokens:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "clip": ("CLIP", {"forceInput": True}),
                "text": ('STRING', {"forceInput": True}),
            }
        }

    RETURN_TYPES = ("INT","INT","INT",)
    RETURN_NAMES = ("g", "l", "t5xxl")

    FUNCTION = "count_tokens"
    CATEGORY = "ftechmax/Text/Tokens"

    def get_token_count(self, tokens):
        bos_token_id = 49406
        eos_token_id = 49407
        t5xxl_eos_token_id=1

        token_counts = {
            'g': 0,
            'l': 0,
            't5xxl': 0
        }
        
        # Filter out padding tokens
        for key, value in tokens.items():
            if key == 't5xxl':
                for token, _ in value[0]:
                    if token == t5xxl_eos_token_id:
                        break
                    else:
                        token_counts[key] += 1
            else:
                count_list = []
                for sub in value:
                    # Find index of first 49406
                    start_index = next(i for i, x in enumerate(sub) if x[0] == bos_token_id)
                    # Find index of first 49407 that comes after 49406
                    end_index = next(i for i, x in enumerate(sub) if x[0] == eos_token_id and i > start_index)
                    count_in_between = (end_index - start_index - 1)
                    count_list.append(count_in_between)
                token_counts[key] = sum(count_list)
        return token_counts

    def count_tokens(self, clip, text):
        print("Counting Tokens for text:", text)
        tokens = clip.tokenize(text)
        token_counts = self.get_token_count(tokens)

        return (token_counts['g'], token_counts['l'], token_counts['t5xxl'])
        
    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("NaN")

class Florence2toCoordinates:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "data": ("JSON", ),
                "index": ("STRING", {"default": "0"}),
                "batch": ("BOOLEAN", {"default": False}),
            },
        }

    RETURN_TYPES = ("STRING", "BBOX")
    RETURN_NAMES =("center_coordinates", "bboxes")
    FUNCTION = "segment"
    CATEGORY = "SAM2"

    def segment(self, data, index, batch=False):
        print(data)
        try:
            coordinates = coordinates.replace("'", '"')
            coordinates = json.loads(coordinates)
        except:
            coordinates = data
        print("Type of data:", type(data))
        print("Data:", data)
        if len(data)==0:
            return (json.dumps([{'x': 0, 'y': 0}]),)
        center_points = []

        if index.strip():  # Check if index is not empty
            indexes = [int(i) for i in index.split(",")]
        else:  # If index is empty, use all indices from data[0]
            indexes = list(range(len(data[0])))

        print("Indexes:", indexes)
        bboxes = []

        if batch:
            for idx in indexes:
                if 0 <= idx < len(data[0]):
                    for i in range(len(data)):
                        bbox = data[i][idx]
                        min_x, min_y, max_x, max_y = bbox
                        center_x = int((min_x + max_x) / 2)
                        center_y = int((min_y + max_y) / 2)
                        center_points.append({"x": center_x, "y": center_y})
                        bboxes.append(bbox)
        else:
            for idx in indexes:
                if 0 <= idx < len(data[0]):
                    bbox = data[0][idx]
                    min_x, min_y, max_x, max_y = bbox
                    center_x = int((min_x + max_x) / 2)
                    center_y = int((min_y + max_y) / 2)
                    center_points.append({"x": center_x, "y": center_y})
                    bboxes.append(bbox)
                else:
                    raise ValueError(f"There's nothing in index: {idx}")

        coordinates = json.dumps(center_points)
        print("Coordinates:", coordinates)
        return (coordinates, bboxes)
