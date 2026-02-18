import os
import json
from aiohttp import web
from server import PromptServer

# 定义数据文件路径 (存放在插件目录下)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(CURRENT_DIR, "huixin_prompts.json")

# ================= API 路由注册 =================
# 注册 API 接口，供前端 JS 调用以保存/读取数据
@PromptServer.instance.routes.get("/huixin/data")
async def get_data(request):
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return web.json_response(data)
        except Exception:
            return web.json_response({"groups": [], "prompts": []})
    return web.json_response({"groups": [], "prompts": []})

@PromptServer.instance.routes.post("/huixin/save")
async def save_data(request):
    try:
        data = await request.json()
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return web.json_response({"status": "success"})
    except Exception as e:
        return web.json_response({"status": "error", "message": str(e)})
# ===============================================

class HuiXin_Prompt_Library:
    """
    汇心提示词库节点
    """
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                # 这是一个多行文本框，JS 会把选中的提示词填进去
                "text": ("STRING", {"multiline": True, "dynamicPrompts": True, "height": 200}),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "do_process"
    CATEGORY = "汇心工具箱"
    
    # 必须定义这个名字，JS 通过这个名字识别节点
    OUTPUT_NODE = True

    def do_process(self, text, unique_id):
        return (text,)