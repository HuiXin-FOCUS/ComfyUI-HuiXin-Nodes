import torch
import numpy as np
from PIL import Image, ImageDraw

class CropByMaskV2:
    """
    Crops a square region from an image based on the bounding box of a mask.
    The crop is always centered on the mask's center and outputs a square image.
    """
    
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        detect_mode = ['mask_area', 'min_bounding_rect', 'max_inscribed_rect']
        multiple_list = ['8', '16', '32', '64', '128', '256', '512', 'None']
        return {
            "required": {
                "image": ("IMAGE",),
                "mask": ("MASK",),
                "invert_mask": ("BOOLEAN", {"default": False}),
                "detect": (detect_mode,),
                "expand_pixels": ("INT", {"default": 0, "min": -9999, "max": 9999, "step": 1}),
                "round_to_multiple": (multiple_list,),
            },
            "optional": {
                "crop_box": ("BOX",),
            }
        }

    RETURN_TYPES = ("IMAGE", "MASK", "MASK", "BOX", "IMAGE")
    RETURN_NAMES = ("cropped_image", "cropped_mask", "box_mask", "crop_box", "box_preview")
    FUNCTION = "crop_by_mask_v2"
    # 你可以根据需要修改这里的分类名称，例如改为 "HuiXin/Image"
    CATEGORY = "HuiXin/Image"

    def tensor_to_pil(self, tensor):
        """Convert tensor to PIL Image with proper format handling"""
        if tensor.dim() == 4:
            tensor = tensor[0]  # Take first batch item
        
        # Handle different tensor formats
        if tensor.dim() == 3:
            # RGB image: (C, H, W) or (H, W, C)
            if tensor.shape[0] == 3:  # (C, H, W)
                tensor = tensor.permute(1, 2, 0)
            elif tensor.shape[2] == 3:  # (H, W, C)
                pass  # Already in correct format
            tensor = tensor.cpu().float()
            if tensor.max() <= 1.0:
                tensor = tensor * 255
            tensor = tensor.to(torch.uint8)
            np_image = tensor.numpy()
            return Image.fromarray(np_image)
        elif tensor.dim() == 2:
            # Grayscale or mask: (H, W)
            tensor = tensor.cpu().float()
            if tensor.max() <= 1.0:
                tensor = tensor * 255
            tensor = tensor.to(torch.uint8)
            np_image = tensor.numpy()
            return Image.fromarray(np_image, mode='L')
        else:
            raise ValueError(f"Unsupported tensor shape: {tensor.shape}")

    def pil_to_tensor(self, image):
        """Convert PIL Image to tensor in ComfyUI format"""
        if isinstance(image, Image.Image):
            if image.mode == 'L':
                # Grayscale image
                np_image = np.array(image).astype(np.float32) / 255.0
                tensor = torch.from_numpy(np_image).unsqueeze(0).unsqueeze(-1)
            else:
                # RGB image
                np_image = np.array(image.convert('RGB')).astype(np.float32) / 255.0
                tensor = torch.from_numpy(np_image).unsqueeze(0)
            
            # ComfyUI expects (batch, height, width, channels)
            return tensor
        return image

    def image_to_mask(self, image):
        """Convert PIL Image to mask tensor in ComfyUI format"""
        if isinstance(image, Image.Image):
            if image.mode != 'L':
                image = image.convert('L')
            np_mask = np.array(image).astype(np.float32) / 255.0
            tensor = torch.from_numpy(np_mask).unsqueeze(0).unsqueeze(-1)
            return tensor
        return image

    def min_bounding_rect(self, mask):
        """Find minimum bounding rectangle of mask"""
        mask_array = np.array(mask)
        coords = np.column_stack(np.where(mask_array > 0))
        if len(coords) == 0:
            return (0, 0, mask.width, mask.height)
        y_min, x_min = coords.min(axis=0)
        y_max, x_max = coords.max(axis=0)
        return (x_min, y_min, x_max - x_min + 1, y_max - y_min + 1)

    def max_inscribed_rect(self, mask):
        """Find maximum inscribed rectangle in mask"""
        # Simplified implementation - use min_bounding_rect as fallback
        return self.min_bounding_rect(mask)

    def mask_area(self, mask):
        """Find mask area bounding box"""
        return self.min_bounding_rect(mask)

    def draw_rect(self, image, x, y, width, height, line_color="#FFFFFF", line_width=2):
        """Draw rectangle on image"""
        draw = ImageDraw.Draw(image)
        draw.rectangle([x, y, x + width, y + height], outline=line_color, width=line_width)
        return image

    def num_round_up_to_multiple(self, number, multiple):
        """Round number up to nearest multiple"""
        return ((number + multiple - 1) // multiple) * multiple

    def crop_by_mask_v2(self, image, mask, invert_mask, detect, expand_pixels, round_to_multiple, crop_box=None):
        ret_images = []
        ret_masks = []
        ret_box_masks = []
        
        # 处理mask
        if mask.dim() == 2:
            mask = mask.unsqueeze(0)
        
        # 如果有多张mask输入，使用第一张
        if mask.shape[0] > 1:
            print(f"Warning: Multiple mask inputs, using the first.")
            mask = mask[0].unsqueeze(0)
        
        if invert_mask:
            mask = 1 - mask

        # 获取画布尺寸
        B, H, W, C = image.shape
        canvas_width, canvas_height = W, H
        
        # 创建预览图像（使用第一张图像）
        preview_image = self.tensor_to_pil(image[0]).convert('RGB')
        
        if crop_box is None:
            # 将mask转换为PIL图像进行处理
            mask_pil = self.tensor_to_pil(mask[0]).convert('L')
            
            if detect == "min_bounding_rect":
                (x, y, w, h) = self.min_bounding_rect(mask_pil)
            elif detect == "max_inscribed_rect":
                (x, y, w, h) = self.max_inscribed_rect(mask_pil)
            else:
                (x, y, w, h) = self.mask_area(mask_pil)

            # 计算中心点
            cx = x + w / 2
            cy = y + h / 2
            
            # 计算正方形边长（取宽高中的最大值）
            size = max(w, h)
            
            # 应用扩展
            final_size = int(size + (expand_pixels * 2))
            half_size = final_size // 2
            
            # 计算裁剪坐标
            crop_x1 = int(cx - half_size)
            crop_y1 = int(cy - half_size)
            crop_x2 = crop_x1 + final_size
            crop_y2 = crop_y1 + final_size
            
            # 处理边界情况
            if crop_x1 < 0:
                crop_x2 -= crop_x1
                crop_x1 = 0
            if crop_y1 < 0:
                crop_y2 -= crop_y1
                crop_y1 = 0
            if crop_x2 > canvas_width:
                crop_x1 -= (crop_x2 - canvas_width)
                crop_x2 = canvas_width
            if crop_y2 > canvas_height:
                crop_y1 -= (crop_y2 - canvas_height)
                crop_y2 = canvas_height
            
            # 确保仍然是正方形
            current_width = crop_x2 - crop_x1
            current_height = crop_y2 - crop_y1
            if current_width != current_height:
                final_size = min(current_width, current_height)
                crop_x2 = crop_x1 + final_size
                crop_y2 = crop_y1 + final_size

            # 圆整到指定倍数
            if round_to_multiple != 'None':
                multiple = int(round_to_multiple)
                width = crop_x2 - crop_x1
                height = crop_y2 - crop_y1
                
                # 计算需要增加的大小
                new_width = self.num_round_up_to_multiple(width, multiple)
                new_height = self.num_round_up_to_multiple(height, multiple)
                
                # 保持正方形，取较大的尺寸
                new_size = max(new_width, new_height)
                
                # 调整裁剪框，保持中心点不变
                crop_x1 = crop_x1 - (new_size - width) // 2
                crop_y1 = crop_y1 - (new_size - height) // 2
                crop_x2 = crop_x1 + new_size
                crop_y2 = crop_y1 + new_size
                
                # 再次检查边界
                if crop_x1 < 0:
                    crop_x2 -= crop_x1
                    crop_x1 = 0
                if crop_y1 < 0:
                    crop_y2 -= crop_y1
                    crop_y1 = 0
                if crop_x2 > canvas_width:
                    crop_x1 -= (crop_x2 - canvas_width)
                    crop_x2 = canvas_width
                if crop_y2 > canvas_height:
                    crop_y1 -= (crop_y2 - canvas_height)
                    crop_y2 = canvas_height

            print(f"Square box detected. x={crop_x1}, y={crop_y1}, size={crop_x2-crop_x1}")
            crop_box = (crop_x1, crop_y1, crop_x2, crop_y2)
            
            # 绘制检测到的原始区域（红色）
            preview_image = self.draw_rect(preview_image, x, y, w, h, line_color="#FF0000",
                                          line_width=max(2, (w + h) // 100))
        
        # 绘制最终的裁剪框（绿色）
        preview_image = self.draw_rect(preview_image, crop_box[0], crop_box[1],
                                      crop_box[2] - crop_box[0], crop_box[3] - crop_box[1],
                                      line_color="#00FF00",
                                      line_width=max(2, (crop_box[2] - crop_box[0] + crop_box[3] - crop_box[1]) // 200))
        
        # 执行裁剪
        for i in range(len(image)):
            img_tensor = image[i]
            mask_tensor = mask[0] if i < mask.shape[0] else mask[0]  # 使用第一张mask或循环使用
            
            # 转换为PIL进行裁剪
            img_pil = self.tensor_to_pil(img_tensor).convert('RGB')
            mask_pil = self.tensor_to_pil(mask_tensor).convert('L')
            
            # 执行裁剪
            cropped_img = img_pil.crop(crop_box)
            cropped_mask = mask_pil.crop(crop_box)
            
            # 转换回tensor - 确保格式正确
            img_tensor_out = self.pil_to_tensor(cropped_img)
            
            # 根据 square_crop 的逻辑创建 cropped_mask
            # 这个 mask 表示裁剪图像的有效区域（1表示图像区域，0表示填充区域）
            crop_width = crop_box[2] - crop_box[0]
            crop_height = crop_box[3] - crop_box[1]
            
            # 计算是否需要填充
            pad_left = max(0, -crop_box[0])
            pad_top = max(0, -crop_box[1])
            pad_right = max(0, crop_box[2] - canvas_width)
            pad_bottom = max(0, crop_box[3] - canvas_height)
            
            # 创建 cropped_mask（类似 square_crop 中的逻辑）
            crop_mask = torch.ones((crop_height, crop_width), dtype=torch.float32)
            
            # 如果有填充区域，将填充区域设为0
            if pad_left > 0 or pad_top > 0 or pad_right > 0 or pad_bottom > 0:
                valid_x = pad_left
                valid_y = pad_top
                valid_w = crop_width - pad_left - pad_right
                valid_h = crop_height - pad_top - pad_bottom
                
                if valid_w > 0 and valid_h > 0:
                    # 重置整个mask为0
                    crop_mask.zero_()
                    # 设置有效区域为1
                    crop_mask[valid_y:valid_y+valid_h, valid_x:valid_x+valid_w] = 1.0
            
            # 转换为 ComfyUI mask 格式 (batch, height, width, 1)
            crop_mask = crop_mask.unsqueeze(0).unsqueeze(-1)
            
            # 创建 box_mask（类似 square_crop 中的逻辑）
            # 全画布大小的 mask，裁剪框位置为白色
            box_mask_full = torch.zeros((H, W), dtype=torch.float32)
            
            # 计算裁剪框在画布上的有效区域
            m_x1 = max(0, crop_box[0])
            m_y1 = max(0, crop_box[1])
            m_x2 = min(W, crop_box[2])
            m_y2 = min(H, crop_box[3])
            
            # 在有效区域内设置值为1.0
            if m_x2 > m_x1 and m_y2 > m_y1:
                box_mask_full[m_y1:m_y2, m_x1:m_x2] = 1.0
            
            # 转换为 ComfyUI mask 格式 (batch, height, width, 1)
            box_mask_full = box_mask_full.unsqueeze(0).unsqueeze(-1)
            
            ret_images.append(img_tensor_out)
            ret_masks.append(crop_mask)
            ret_box_masks.append(box_mask_full)

        print(f"Processed {len(ret_images)} image(s).")
        
        # 确保输出格式正确 - ComfyUI 需要正确的张量形状
        if len(ret_images) > 1:
            output_images = torch.cat(ret_images, dim=0)
            output_masks = torch.cat(ret_masks, dim=0)
            output_box_masks = torch.cat(ret_box_masks, dim=0)
        else:
            output_images = ret_images[0]
            output_masks = ret_masks[0]
            output_box_masks = ret_box_masks[0]
        
        # 预览图像也需要正确格式
        preview_tensor = self.pil_to_tensor(preview_image)
        
        return (output_images, output_masks, output_box_masks, list(crop_box), preview_tensor)