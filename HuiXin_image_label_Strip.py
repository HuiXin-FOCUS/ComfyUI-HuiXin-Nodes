import torch
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageColor
import os
import platform

# --- 字体扫描逻辑保持不变 ---
def get_system_font_paths():
    font_paths = {}
    search_paths = []
    current_dir = os.path.dirname(os.path.abspath(__file__))
    local_fonts_dir = os.path.join(current_dir, "fonts")
    if not os.path.exists(local_fonts_dir):
        try:
            os.makedirs(local_fonts_dir)
        except:
            pass
    search_paths.append(local_fonts_dir)

    system = platform.system()
    if system == "Windows":
        search_paths.append(os.path.join(os.environ["WINDIR"], "Fonts"))
    elif system == "Darwin":
        search_paths.append("/Library/Fonts")
        search_paths.append("/System/Library/Fonts")
        search_paths.append(os.path.expanduser("~/Library/Fonts"))
    elif system == "Linux":
        search_paths.append("/usr/share/fonts")
        search_paths.append(os.path.expanduser("~/.local/share/fonts"))

    for path in search_paths:
        if os.path.exists(path):
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file.lower().endswith((".ttf", ".otf")):
                        if file not in font_paths:
                            font_paths[file] = os.path.join(root, file)
    return font_paths

FONT_MAP = get_system_font_paths()
FONT_LIST = sorted(list(FONT_MAP.keys()))
if not FONT_LIST:
    FONT_LIST = ["arial.ttf"]
    FONT_MAP = {"arial.ttf": "arial.ttf"}

class ImageLabelStrip:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                # 修改点：将 default 改为 placeholder，使其变成灰色提示文字
                "text_content": ("STRING", {
                    "multiline": True, 
                    "placeholder": "在此输入标签内容..." 
                }),
                "font_file": (FONT_LIST, ), 
                "font_size": ("INT", {"default": 40, "min": 10, "max": 500, "step": 1}),
                "strip_height": ("INT", {"default": 100, "min": 10, "max": 1000, "step": 10}),
                "strip_color_hex": ("STRING", {"default": "#FFFFFF"}),
                "text_color_hex": ("STRING", {"default": "#000000"}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "add_label"
    CATEGORY = "HuiXin/Image"

    def add_label(self, image, text_content, font_file, font_size, strip_height, strip_color_hex, text_color_hex):
        # 如果 text_content 为空（用户没填），则不绘制文字或设为空字符串
        if text_content is None:
            text_content = ""

        result_images = []
        try:
            strip_color = ImageColor.getrgb(strip_color_hex)
        except:
            strip_color = (255, 255, 255)
        try:
            text_color = ImageColor.getrgb(text_color_hex)
        except:
            text_color = (0, 0, 0)

        font_path = FONT_MAP.get(font_file, font_file)
        try:
            font = ImageFont.truetype(font_path, font_size)
        except:
            font = ImageFont.load_default()

        for i in image:
            img_tensor = i.cpu().numpy() * 255.0
            img_tensor = np.clip(img_tensor, 0, 255).astype(np.uint8)
            original_img = Image.fromarray(img_tensor)

            width, height = original_img.size
            new_height = height + strip_height
            new_img = Image.new("RGB", (width, new_height), strip_color)
            new_img.paste(original_img, (0, 0))

            if text_content.strip(): # 只有在有内容时才进行绘制绘制
                draw = ImageDraw.Draw(new_img)
                
                # 计算文字居中逻辑
                left, top, right, bottom = draw.textbbox((0, 0), text_content, font=font)
                text_w = right - left
                text_h = bottom - top
                
                text_x = (width - text_w) // 2
                text_y = height + (strip_height - text_h) // 2 - top

                draw.text((text_x, text_y), text_content, font=font, fill=text_color)

            img_out = np.array(new_img).astype(np.float32) / 255.0
            img_out = torch.from_numpy(img_out)
            result_images.append(img_out)

        return (torch.stack(result_images, dim=0),)