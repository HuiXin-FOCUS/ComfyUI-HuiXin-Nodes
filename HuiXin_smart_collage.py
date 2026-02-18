import torch
import numpy as np
from PIL import Image, ImageOps
import math

class HuiXin_Smart_Collage:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                # 间距设置
                "gap": ("INT", {"default": 10, "min": 0, "max": 500, "step": 1}),
                # 背景颜色 (R, G, B)
                "background_color": ("STRING", {"default": "#FFFFFF"}), 
                # 布局模式 (新增了 Masonry 选项)
                "layout_mode": ([
                    "Smart Grid (智能网格)", 
                    "Horizontal (水平横排)", 
                    "Vertical (垂直竖排)",
                    "Masonry (瀑布流/紧凑布局)"  # <--- 新增的选项在这里
                ],),
                # 缩放模式
                "scaling_method": (["Crop to Fit (裁剪填充)", "Pad to Fit (保持完整-留白)"],),
                # --- 尺寸限制 (0表示不限制) ---
                "width": ("INT", {"default": 0, "min": 0, "max": 8192, "step": 1, "display": "number"}),
                "height": ("INT", {"default": 0, "min": 0, "max": 8192, "step": 1, "display": "number"}),
            },
            "optional": {
                "image_1": ("IMAGE",),
                "image_2": ("IMAGE",),
                "image_3": ("IMAGE",),
                "image_4": ("IMAGE",),
                "image_5": ("IMAGE",), 
                "image_6": ("IMAGE",),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "collage_images"
    CATEGORY = "HuiXin/Image"

    def collage_images(self, gap, background_color, layout_mode, scaling_method, width, height, **kwargs):
        # 1. 收集所有非空的输入图像
        input_images = []
        for key in sorted(kwargs.keys()):
            if key.startswith("image_") and kwargs[key] is not None:
                input_images.append(kwargs[key])
        
        if not input_images:
            return (torch.zeros((1, 512, 512, 3)),)

        # 2. Tensor 转 PIL
        pil_images = []
        for tensor_img in input_images:
            i = 255. * tensor_img.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8)[0])
            pil_images.append(img)

        # 解析颜色
        bg_color = self.hex_to_rgb(background_color)
        
        # 3. 根据不同模式进行初步拼图
        final_image = None

        if layout_mode == "Horizontal (水平横排)":
            final_image = self.process_horizontal(pil_images, gap, bg_color)
        elif layout_mode == "Vertical (垂直竖排)":
            final_image = self.process_vertical(pil_images, gap, bg_color)
        elif layout_mode == "Masonry (瀑布流/紧凑布局)": # <--- 新增分支
            final_image = self.process_masonry(pil_images, gap, bg_color)
        else: # Smart Grid
            final_image = self.process_grid(pil_images, gap, bg_color, scaling_method)

        # 4. 调整到目标尺寸 (如果设置了)
        if width > 0 or height > 0:
            final_image = self.resize_to_target(final_image, width, height, scaling_method, bg_color)

        # 5. 转回 Tensor
        img_np = np.array(final_image).astype(np.float32) / 255.0
        img_tensor = torch.from_numpy(img_np).unsqueeze(0)

        return (img_tensor,)

    # --- 统一调整最终尺寸的逻辑 ---
    def resize_to_target(self, img, t_w, t_h, method, bg_color):
        if t_w == 0 and t_h > 0:
            ratio = t_h / img.height
            t_w = int(img.width * ratio)
        elif t_h == 0 and t_w > 0:
            ratio = t_w / img.width
            t_h = int(img.height * ratio)
        
        if method == "Crop to Fit (裁剪填充)":
            result = ImageOps.fit(img, (t_w, t_h), method=Image.Resampling.LANCZOS)
        else:
            resized_img = ImageOps.contain(img, (t_w, t_h), method=Image.Resampling.LANCZOS)
            result = Image.new("RGB", (t_w, t_h), bg_color)
            x = (t_w - resized_img.width) // 2
            y = (t_h - resized_img.height) // 2
            result.paste(resized_img, (x, y))
        return result

    # --- 水平横排 ---
    def process_horizontal(self, images, gap, bg_color):
        base_h = images[0].height
        resized_imgs = []
        total_width = 0
        for img in images:
            aspect = img.width / img.height
            new_w = int(base_h * aspect)
            resized = img.resize((new_w, base_h), Image.Resampling.LANCZOS)
            resized_imgs.append(resized)
            total_width += new_w
            
        total_width += (len(images) - 1) * gap
        canvas = Image.new("RGB", (total_width, base_h), bg_color)
        current_x = 0
        for img in resized_imgs:
            canvas.paste(img, (current_x, 0))
            current_x += img.width + gap
        return canvas

    # --- 垂直竖排 ---
    def process_vertical(self, images, gap, bg_color):
        base_w = images[0].width
        resized_imgs = []
        total_height = 0
        for img in images:
            aspect = img.height / img.width
            new_h = int(base_w * aspect)
            resized = img.resize((base_w, new_h), Image.Resampling.LANCZOS)
            resized_imgs.append(resized)
            total_height += new_h
            
        total_height += (len(images) - 1) * gap
        canvas = Image.new("RGB", (base_w, total_height), bg_color)
        current_y = 0
        for img in resized_imgs:
            canvas.paste(img, (0, current_y))
            current_y += img.height + gap
        return canvas

    # --- 新增逻辑：瀑布流 (Masonry) ---
    def process_masonry(self, images, gap, bg_color):
        count = len(images)
        # 根据图片数量自动决定列数 (类似 Smart Grid 的逻辑)
        cols = math.ceil(math.sqrt(count))
        if cols < 2 and count > 1: cols = 2 # 至少2列，除非只有1张图
        
        # 以第一张图的宽度作为基准列宽 (也可以设固定值，这里用相对值更灵活)
        col_w = images[0].width
        
        # 1. 预处理：将所有图片等宽缩放
        resized_imgs = []
        for img in images:
            aspect = img.height / img.width
            new_h = int(col_w * aspect)
            resized = img.resize((col_w, new_h), Image.Resampling.LANCZOS)
            resized_imgs.append(resized)
            
        # 2. 计算位置：将图片分配到当前高度最小的列
        col_heights = [0] * cols
        col_items = [[] for _ in range(cols)] # 存储每列的图片 [(img, y_pos), ...]
        
        for img in resized_imgs:
            # 找到当前最短的一列
            min_col_idx = col_heights.index(min(col_heights))
            
            # 记录位置
            y_pos = col_heights[min_col_idx]
            col_items[min_col_idx].append((img, y_pos))
            
            # 更新该列高度
            col_heights[min_col_idx] += img.height + gap
            
        # 3. 创建画布
        # 宽度 = 列宽总和 + 间隙总和
        total_w = cols * col_w + (cols - 1) * gap
        # 高度 = 最长列的高度 (减去最后一个多余的gap)
        max_h = max(col_heights)
        if max_h > gap: max_h -= gap
        
        canvas = Image.new("RGB", (total_w, max_h), bg_color)
        
        # 4. 粘贴图片
        for col_idx, items in enumerate(col_items):
            x_pos = col_idx * (col_w + gap)
            for img, y_pos in items:
                canvas.paste(img, (x_pos, y_pos))
                
        return canvas

    # --- 智能网格 ---
    def process_grid(self, images, gap, bg_color, method):
        count = len(images)
        cols = math.ceil(math.sqrt(count))
        rows = math.ceil(count / cols)
        cell_w, cell_h = images[0].size
        
        processed_imgs = []
        for img in images:
            if method == "Crop to Fit (裁剪填充)":
                processed = ImageOps.fit(img, (cell_w, cell_h), method=Image.Resampling.LANCZOS)
            else:
                processed = ImageOps.contain(img, (cell_w, cell_h), method=Image.Resampling.LANCZOS)
                bg_cell = Image.new("RGB", (cell_w, cell_h), bg_color)
                paste_x = (cell_w - processed.width) // 2
                paste_y = (cell_h - processed.height) // 2
                bg_cell.paste(processed, (paste_x, paste_y))
                processed = bg_cell
            processed_imgs.append(processed)

        canvas_w = cols * cell_w + (cols - 1) * gap
        canvas_h = rows * cell_h + (rows - 1) * gap
        canvas = Image.new("RGB", (canvas_w, canvas_h), bg_color)

        for idx, img in enumerate(processed_imgs):
            row_idx = idx // cols
            col_idx = idx % cols
            x = col_idx * (cell_w + gap)
            y = row_idx * (cell_h + gap)
            canvas.paste(img, (x, y))
            
        return canvas

    def hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 6:
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        else:
            return (255, 255, 255)