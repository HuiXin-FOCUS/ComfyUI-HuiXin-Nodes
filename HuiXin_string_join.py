# HuiXin_string_join.py

class HuiXin_String_Join:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                # 接收上游传来的字符串列表
                "text_list": ("STRING", {"forceInput": True}),
                # 设置合并的分隔符
                "separator": ("STRING", {"default": "\\n\\n", "multiline": False}),
            }
        }

    # 开启此项，节点才能一次性接住整个字符串列表
    INPUT_IS_LIST = True
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("combined_string",)
    FUNCTION = "join_strings"
    CATEGORY = "HuiXin/Utils"

    def join_strings(self, text_list, separator):
        # 【修正点】因为开启了 INPUT_IS_LIST，separator 也会被包装成列表，例如 ["\\n\\n"]
        # 我们需要先取出里面的字符串
        real_separator = separator[0] if isinstance(separator, list) else separator
        
        # 处理转义字符
        sep = real_separator.replace("\\n", "\n").replace("\\r", "\r").replace("\\t", "\t")
        
        if not text_list:
            return ("",)
            
        # text_list 本身已经是一个列表了 ['str1', 'str2', ...]
        # 将所有项合并
        combined = sep.join([str(t) for t in text_list])
        
        # 注意：由于 INPUT_IS_LIST 为 True，返回值也必须包裹在列表里
        return [combined]

NODE_CLASS_MAPPINGS = {
    "HuiXin_String_Join": HuiXin_String_Join
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "HuiXin_String_Join": "汇心字符串合并"
}