import requests
import json
import base64
import io
import torch
import numpy as np
from PIL import Image

def tensor2base64(image):
    if isinstance(image, torch.Tensor):
        image = image.cpu().numpy()
    if len(image.shape) == 4: image = image[0]
    i = 255. * image
    img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG", quality=90)
    return f"data:image/jpeg;base64,{base64.b64encode(buffered.getvalue()).decode('utf-8')}"

class HuiXin_Vision_LLM:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):
        models = ["gemini-2.5-flash", "gemini-2.5-pro", "nano-banana", "gpt-4o-mini", "qwen-vl-max", "claude-3-5-sonnet-20240620"]
        return {
            "required": {
                "image": ("IMAGE",),
                "channel": (["Grsai", "ModelScope (魔搭)", "Allapi (云雾)"], {"default": "Grsai"}),
                "grsai_api_key": ("STRING", {"default": "", "placeholder": "Grsai Key"}),
                "modelscope_api_key": ("STRING", {"default": "", "placeholder": "ModelScope Key"}),
                "allapi_api_key": ("STRING", {"default": "", "placeholder": "Allapi Key"}),
                "model": (models, {"default": "gemini-2.5-flash"}),
                "system_prompt": ("STRING", {"multiline": True, "default": "你是一名专业的提示词描述助手", "height": 60}),
                "user_prompt": ("STRING", {"multiline": True, "default": "详细描述图片", "height": 60}),
                "max_tokens": ("INT", {"default": 1024}),
                "temperature": ("FLOAT", {"default": 0.7, "min": 0, "max": 2}),
                "seed": ("INT", {"default": -1}),
            },
            "optional": {"image_2": ("IMAGE",), "image_3": ("IMAGE",)}
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("description",)
    FUNCTION = "gen_description"
    CATEGORY = "HuiXin/LLM" # 统一分类

    def gen_description(self, image, channel, grsai_api_key, modelscope_api_key, allapi_api_key, model, system_prompt, user_prompt, max_tokens, temperature, seed, image_2=None, image_3=None):
        urls = {
            "Grsai": ("https://grsaiapi.com/v1/chat/completions", grsai_api_key),
            "ModelScope (魔搭)": ("https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions", modelscope_api_key),
            "Allapi (云雾)": ("https://api.allapi.store/v1/chat/completions", allapi_api_key)
        }
        api_url, api_key = urls.get(channel)
        if not api_key: return (f"错误: 缺少 {channel} 的 API Key",)

        content = [{"type": "text", "text": user_prompt}]
        for img in [image, image_2, image_3]:
            if img is not None:
                content.append({"type": "image_url", "image_url": {"url": tensor2base64(img)}})

        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {
            "model": model,
            "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": content}],
            "max_tokens": max_tokens, "temperature": temperature
        }
        if seed != -1: payload["seed"] = seed

        try:
            # 增加 timeout 保护，防止卡死
            response = requests.post(api_url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            res_data = response.json()
            return (res_data['choices'][0]['message']['content'],)
        except Exception as e:
            return (f"请求失败: {str(e)}",)