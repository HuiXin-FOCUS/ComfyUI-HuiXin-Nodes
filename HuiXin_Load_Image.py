import os
import hashlib
import torch
import numpy as np
from PIL import Image, ImageOps, ImageSequence
import folder_paths
import node_helpers

class HuiXin_Load_Image:
    @classmethod
    def INPUT_TYPES(s):
        input_dir = folder_paths.get_input_directory()
        files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))] if os.path.exists(input_dir) else []
        return {
            "required": {
                "image": (sorted(files), {"image_upload": True})
            },
        }

    CATEGORY = "HuiXin/Image"
    RETURN_TYPES = ("IMAGE", "MASK")
    RETURN_NAMES = ("image", "mask")
    FUNCTION = "load_image"

    def load_image(self, image):
        # 只要没有图片路径，直接返回 64x64 黑块
        if not image or image == "":
            return self.get_empty_image()

        image_path = folder_paths.get_annotated_filepath(image)
        if image_path is None or not os.path.exists(image_path):
            return self.get_empty_image()

        try:
            img = node_helpers.pillow(Image.open, image_path)
            output_images = []
            output_masks = []
            for i in ImageSequence.Iterator(img):
                i = ImageOps.exif_transpose(i)
                image_rgb = i.convert("RGB")
                image_np = np.array(image_rgb).astype(np.float32) / 255.0
                output_images.append(torch.from_numpy(image_np)[None,])
                if 'A' in i.getbands():
                    mask = 1. - torch.from_numpy(np.array(i.getchannel('A')).astype(np.float32) / 255.0)
                else:
                    mask = torch.zeros((i.height, i.width), dtype=torch.float32)
                output_masks.append(mask.unsqueeze(0))
            return (torch.cat(output_images, dim=0), torch.cat(output_masks, dim=0))
        except:
            return self.get_empty_image()

    def get_empty_image(self):
        # 返回 64x64 黑色占位图
        return (torch.zeros((1, 64, 64, 3), dtype=torch.float32), torch.zeros((1, 64, 64), dtype=torch.float32))

    @classmethod
    def IS_CHANGED(s, image):
        # 只要图片路径为空，就返回一个唯一值触发后端更新
        if not image:
            return "cleared"
        image_path = folder_paths.get_annotated_filepath(image)
        if image_path and os.path.exists(image_path):
            m = hashlib.sha256()
            with open(image_path, 'rb') as f:
                m.update(f.read())
            return m.digest().hex()
        return "changed"

    @classmethod
    def VALIDATE_INPUTS(s, image):
        return True