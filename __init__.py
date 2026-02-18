import os

# 导入节点类
from .HuiXin_vision_llm import HuiXin_Vision_LLM
from .HuiXin_prompt_library import HuiXin_Prompt_Library
from .HuiXin_square_crop import CropByMaskV2 as HuiXin_Square_Crop_By_Mask
from .HuiXin_image_label_Strip import ImageLabelStrip
from .HuiXin_smart_collage import HuiXin_Smart_Collage
from .HuiXin_Detail_Page_Preset import HuiXin_Detail_Page_Preset
from .HuiXin_Load_Image import HuiXin_Load_Image
from .HuiXin_NanoBananaPro import HuiXin_NanoBananaPro
from .HuiXin_NanoBananaPro_Batch import HuiXin_NanoBananaPro_Batch
from .HuiXin_string_join import HuiXin_String_Join
from .HuiXin_prompt_splitter import HuiXin_Prompt_Splitter

NODE_CLASS_MAPPINGS = {
    "HuiXin_Vision_LLM": HuiXin_Vision_LLM,
    "HuiXin_Prompt_Library": HuiXin_Prompt_Library,
    "HuiXin_Square_Crop_By_Mask": HuiXin_Square_Crop_By_Mask,
    "HuiXin_Image_Label_Strip": ImageLabelStrip,
    "HuiXin_Smart_Collage": HuiXin_Smart_Collage,
    "HuiXin_Detail_Page_Preset": HuiXin_Detail_Page_Preset,
    "HuiXin_Load_Image": HuiXin_Load_Image,
    "HuiXin_NanoBananaPro": HuiXin_NanoBananaPro,
    "HuiXin_NanoBananaPro_Batch": HuiXin_NanoBananaPro_Batch,
    "HuiXin_String_Join": HuiXin_String_Join,
    "HuiXin_Prompt_Splitter": HuiXin_Prompt_Splitter
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "HuiXin_Vision_LLM": "汇心-多模态LLM反推",
    "HuiXin_Prompt_Library": "汇心-提示词库",
    "HuiXin_Square_Crop_By_Mask": "汇心-方形裁剪",
    "HuiXin_Image_Label_Strip": "汇心-标签条",
    "HuiXin_Smart_Collage": "汇心-智能拼图",
    "HuiXin_Detail_Page_Preset": "汇心-详情页预设",
    "HuiXin_Load_Image": "汇心-加载图像",
    "HuiXin_NanoBananaPro": "汇心-NanoBananaPro",
    "HuiXin_NanoBananaPro_Batch": "汇心-NanoBananaPro批量",
    "HuiXin_String_Join": "汇心-字符串合并",
    "HuiXin_Prompt_Splitter": "汇心-提示词分割"
}

WEB_DIRECTORY = "./web"
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]