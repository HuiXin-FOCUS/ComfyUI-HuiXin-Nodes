import torch
import requests
import time
import numpy as np
from PIL import Image
import io
import concurrent.futures

class HuiXin_NanoBananaPro:
    def __init__(self):
        self.base_url = "https://toapis.com"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True, "default": ""}),
                # 1. 调换位置：先 channel 后 api_key
                "channel": (["ToAPIs"], {"default": "ToAPIs"}),
                "toapis_api_key": ("STRING", {"default": "", "placeholder": "在此输入 ToAPIs Key"}),
                "model": (["gemini-3-pro-image-preview"], {"default": "gemini-3-pro-image-preview"}),
                "aspect_ratio": (["1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9", "auto"], {"default": "auto"}),
                "resolution": (["1K", "2K", "4K", "auto"], {"default": "auto"}),
                "quality": (["high", "standard"], {"default": "high"}),
                "temperature": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 2.0, "step": 0.01}),
                "top_p": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "character_consistency": ("BOOLEAN", {"default": True}),
                "工作流并发": ("BOOLEAN", {"default": False}),
            },
            "optional": {
                "image_1": ("IMAGE",),
                "image_2": ("IMAGE",),
                "image_3": ("IMAGE",),
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("image", "info")
    FUNCTION = "generate"
    CATEGORY = "HuiXin/Generate"

    def tensor_to_pil(self, img_tensor):
        if img_tensor is None: return None
        i = 255. * img_tensor.cpu().numpy().squeeze()
        if i.ndim == 3:
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
        else:
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8), mode='RGB')
        return img

    def upload_image(self, api_key, pil_img):
        buffered = io.BytesIO()
        pil_img.save(buffered, format="PNG")
        files = {"file": ("image.png", buffered.getvalue(), "image/png")}
        headers = {"Authorization": f"Bearer {api_key}"}
        url = f"{self.base_url}/v1/uploads/images"
        try:
            response = requests.post(url, headers=headers, files=files, timeout=30)
            if response.status_code == 200:
                return response.json().get("data", {}).get("url")
        except: pass
        return None

    def _single_task(self, idx, prompt_text, api_key, model, size, res, qual, temp, top_p, seed, consistency, img_urls):
        if idx > 0: time.sleep(idx * 0.1)
        
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {
            "model": model, "prompt": prompt_text, "size": size, "image_urls": img_urls,
            "metadata": {
                "resolution": res, "quality": qual, "seed": seed,
                "temperature": temp, "top_p": top_p, "character_consistency": consistency
            }
        }
        
        try:
            gen_resp = requests.post(f"{self.base_url}/v1/images/generations", headers=headers, json=payload, timeout=30)
            if gen_resp.status_code != 200:
                return None, f"任务{idx+1}提交失败: {gen_resp.text[:50]}"
            task_id = gen_resp.json().get("id")
            
            status_url = f"{self.base_url}/v1/images/generations/{task_id}"
            for _ in range(120):
                time.sleep(4)
                status_resp = requests.get(status_url, headers=headers, timeout=15).json()
                if status_resp.get("status") == "completed":
                    res_obj = status_resp.get("result", {})
                    data_list = res_obj.get("data", [])
                    url = data_list[0].get("url") if data_list else (status_resp.get("url") or status_resp.get("data", {}).get("url"))
                    if url:
                        img_res = requests.get(url, timeout=30)
                        if img_res.status_code == 200:
                            pil_img = Image.open(io.BytesIO(img_res.content)).convert("RGB")
                            return torch.from_numpy(np.array(pil_img).astype(np.float32) / 255.0)[None,], f"任务{idx+1}成功"
                    break
                elif status_resp.get("status") == "failed":
                    return None, f"任务{idx+1}失败: {status_resp.get('fail_reason')}"
        except Exception as e:
            return None, f"任务{idx+1}异常: {str(e)}"
        
        return None, f"任务{idx+1}超时"

    # 注意：这里的参数顺序也随之调整了，以匹配 INPUT_TYPES
    def generate(self, prompt, channel, toapis_api_key, model, aspect_ratio, resolution, 
                 quality, temperature, top_p, seed, character_consistency, 工作流并发,
                 image_1=None, image_2=None, image_3=None):
        
        # 2. 逻辑修改：如果 API Key 为空，直接抛出异常终止运行
        if not toapis_api_key or toapis_api_key.strip() == "":
            raise RuntimeError("【汇心提示】：请输入有效的 ToAPIs API Key，运行已终止。")

        if 工作流并发:
            prompts = [p.strip() for p in prompt.split('\n\n') if p.strip()]
            print(f"NanoBananaPro: 开启并发模式，检测到 {len(prompts)} 段提示词。")
        else:
            prompts = [prompt.strip()]
            print(f"NanoBananaPro: 普通模式，单一任务执行。")

        img_urls = []
        for img_tensor in [image_1, image_2, image_3]:
            if img_tensor is not None:
                pil_img = self.tensor_to_pil(img_tensor)
                url = self.upload_image(toapis_api_key, pil_img)
                if url: img_urls.append(url)

        results = [None] * len(prompts)
        logs = []
        cur_size = aspect_ratio if aspect_ratio != "auto" else "1:1"
        cur_res = resolution if resolution != "auto" else "1K"

        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            future_to_idx = {
                executor.submit(
                    self._single_task, i, p, toapis_api_key, model, cur_size, 
                    cur_res, quality, temperature, top_p, seed, 
                    character_consistency, img_urls
                ): i for i, p in enumerate(prompts)
            }
            
            for future in concurrent.futures.as_completed(future_to_idx):
                idx = future_to_idx[future]
                img, info = future.result()
                results[idx] = img
                logs.append(info)

        final_images = [img for img in results if img is not None]
        if final_images:
            th, tw = final_images[0].shape[1], final_images[0].shape[2]
            processed = []
            for img in final_images:
                if img.shape[1] != th or img.shape[2] != tw:
                    pil = Image.fromarray((img.squeeze().cpu().numpy() * 255).astype(np.uint8))
                    pil = pil.resize((tw, th), Image.LANCZOS)
                    img = torch.from_numpy(np.array(pil).astype(np.float32) / 255.0)[None,]
                processed.append(img)
            return (torch.cat(processed, dim=0), "\n".join(logs))
        else:
            return (torch.zeros((1, 64, 64, 3)), "无有效结果:\n" + "\n".join(logs))