import os
import json
import requests
import time
import torch
import numpy as np
import math
from PIL import Image
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor

# --- 内部工具函数 ---

def resize_image_by_megapixels(pil_img, megapixels):
    width, height = pil_img.size
    current_pixels = width * height
    target_pixels = megapixels * 1_000_000
    if current_pixels > target_pixels:
        scale_factor = math.sqrt(target_pixels / current_pixels)
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)
        return pil_img.resize((new_width, new_height), Image.LANCZOS)
    return pil_img

def pil_to_bytes(pil_img):
    buffer = BytesIO()
    pil_img.convert("RGB").save(buffer, format="JPEG", quality=90)
    return buffer.getvalue()

def tensor_to_pil(tensor):
    image = tensor.cpu().numpy()
    if len(image.shape) == 4:
        image = image[0]
    image = (image * 255).astype(np.uint8)
    return Image.fromarray(image)

def get_files_from_folder(folder_path):
    if not folder_path or not os.path.exists(folder_path):
        return []
    exts = ('.jpg', '.jpeg', '.png', '.webp', '.bmp')
    try:
        files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.lower().endswith(exts)]
        return sorted(files)
    except:
        return []

def split_batch_tensor(tensor):
    if tensor is None:
        return []
    if len(tensor.shape) == 3: # H,W,C
        return [tensor.unsqueeze(0)]
    return [tensor[i:i+1] for i in range(tensor.shape[0])]

# --- 节点类定义 ---

class HuiXin_NanoBananaPro_Batch:
    def __init__(self):
        self.base_url = "https://toapis.com"
        self.api_upload = f"{self.base_url}/v1/uploads/images"
        self.api_submit = f"{self.base_url}/v1/images/generations"
        self.api_query = f"{self.base_url}/v1/images/generations"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True, "default": "", "placeholder": "prompt"}),
                "channel": (["ToAPIs"],),
                "toapis_api_key": ("STRING", {"default": ""}),
                "model": (["gemini-3-pro-image-preview"],),
                "aspect_ratio": (["auto", "1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"],),
                "resolution": (["auto", "1K", "2K", "4K"],),
                "像素缩放": ("BOOLEAN", {"default": False}),
                "像素数量": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 10.0, "step": 0.1}),
                "文件夹1": ("STRING", {"default": ""}),
                "文件夹2": ("STRING", {"default": ""}),
                "文件夹3": ("STRING", {"default": ""}),
                "保存路径": ("STRING", {"default": ""}),
                "图像匹配模式": (["不匹配", "1:1", "1*N"],),
            },
            "optional": {
                "image_1": ("IMAGE",),
                "image_2": ("IMAGE",),
                "image_3": ("IMAGE",),
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("image", "info")
    FUNCTION = "run_batch"
    CATEGORY = "HuiXin-Nodes"

    def run_batch(self, **kwargs):
        prompt = kwargs.get("prompt", "").strip()
        api_key = kwargs.get("toapis_api_key", "").strip()
        
        # --- 新增校验逻辑：如果没有填入，直接抛出异常终止运行 ---
        if not api_key:
            raise ValueError("【汇心提示】：请输入有效的 ToAPIs API Key，运行已终止。")
        if not prompt:
            raise ValueError("【汇心提示】：提示词（Prompt）不能为空，运行已终止。")

        mode = kwargs.get("图像匹配模式")
        save_dir = kwargs.get("保存路径")
        
        # 1. 提取端口输入的图片
        ref_pins = []
        for i in range(1, 4):
            img_tensor = kwargs.get(f"image_{i}")
            if img_tensor is not None:
                ref_pins.extend(split_batch_tensor(img_tensor))
        
        # 2. 获取文件夹内的文件列表
        list1 = get_files_from_folder(kwargs.get("文件夹1"))
        list2 = get_files_from_folder(kwargs.get("文件夹2"))
        list3 = get_files_from_folder(kwargs.get("文件夹3"))
        
        task_groups = []

        # 3. 核心逻辑
        if mode == "1:1":
            max_len = max(len(list1), len(list2), len(list3))
            for i in range(max_len):
                g = []
                if i < len(list1): g.append(list1[i])
                if i < len(list2): g.append(list2[i])
                if i < len(list3): g.append(list3[i])
                g.extend(ref_pins) 
                if g: task_groups.append(g)
        elif mode == "1*N":
            if not list1:
                if ref_pins: task_groups.append(ref_pins)
            else:
                for item1 in list1:
                    if list2:
                        for item2 in list2:
                            g = [item1, item2]
                            if list3: g.append(list3[0])
                            g.extend(ref_pins)
                            task_groups.append(g)
                    else:
                        task_groups.append([item1] + ref_pins)
        else:
            if list1:
                for item in list1:
                    task_groups.append([item] + ref_pins)
            elif ref_pins:
                task_groups.append(ref_pins)

        if not task_groups:
            return (torch.zeros((1, 64, 64, 3)), "未找到有效图片任务")

        final_images = []
        log_info = []

        # 4. 执行上传和请求
        def process_task(img_group):
            headers = {"Authorization": f"Bearer {api_key}"}
            image_urls = []
            
            for item in img_group:
                try:
                    pil_img = Image.open(item) if isinstance(item, str) else tensor_to_pil(item)
                    if kwargs.get("像素缩放"):
                        pil_img = resize_image_by_megapixels(pil_img, kwargs.get("像素数量"))
                    img_bytes = pil_to_bytes(pil_img)
                    files = {'file': ('image.jpg', img_bytes, 'image/jpeg')}
                    up_r = requests.post(self.api_upload, headers=headers, files=files, timeout=30)
                    up_data = up_r.json()
                    if up_r.status_code == 200 and up_data.get("success"):
                        image_urls.append(up_data["data"]["url"])
                    else:
                        return None, f"上传失败: {up_data.get('message', '未知错误')}"
                except Exception as e:
                    return None, f"处理异常: {str(e)}"

            payload = {
                "model": "gemini-3-pro-image-preview",
                "prompt": prompt,
                "size": kwargs.get("aspect_ratio") if kwargs.get("aspect_ratio") != "auto" else "1:1",
                "n": 1,
                "image_urls": image_urls,
                "metadata": {"resolution": kwargs.get("resolution") if kwargs.get("resolution") != "auto" else "1K"}
            }
            
            try:
                resp = requests.post(self.api_submit, json=payload, headers=headers, timeout=30)
                res_json = resp.json()
                if resp.status_code != 200: return None, f"提交失败: {res_json.get('message', resp.text)}"
                
                tid = res_json.get("id")
                for _ in range(120):
                    time.sleep(5)
                    q_r = requests.get(f"{self.api_query}/{tid}", headers=headers)
                    q_data = q_r.json()
                    status = q_data.get("status")
                    if status == "completed":
                        img_url = q_data.get("result", {}).get("data", [])[0].get("url")
                        img_content = requests.get(img_url).content
                        if save_dir and os.path.exists(save_dir):
                            with open(os.path.join(save_dir, f"Nano_{tid.replace(':','_')}.png"), "wb") as f:
                                f.write(img_content)
                        pil_res = Image.open(BytesIO(img_content)).convert("RGB")
                        return torch.from_numpy(np.array(pil_res).astype(np.float32) / 255.0)[None, :, :, :], f"任务 {tid} 成功"
                    elif status == "failed":
                        return None, f"任务失败: {q_data.get('error', {}).get('message', '未知')}"
                return None, "任务超时"
            except Exception as e:
                return None, f"网络错误: {str(e)}"

        # 并发设为 50
        with ThreadPoolExecutor(max_workers=50) as executor:
            results = list(executor.map(process_task, task_groups))

        for img, msg in results:
            if img is not None: final_images.append(img)
            log_info.append(msg)

        if not final_images:
            return (torch.zeros((1, 64, 64, 3)), "全部失败:\n" + "\n".join(log_info))
            
        return (torch.cat(final_images, dim=0), "\n".join(log_info))