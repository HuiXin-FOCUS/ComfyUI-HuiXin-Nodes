import json
import threading
from server import PromptServer
from aiohttp import web

# 用于存储每个节点的等待事件、数据和取消标志
huixin_wait_events = {}
huixin_received_data = {}
huixin_cancel_flags = {}

class HuiXin_Prompt_Splitter:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "line_text": ("STRING", {"forceInput": True}),
                "删除空行": ("BOOLEAN", {"default": True}),
                "删除首尾空白": ("BOOLEAN", {"default": True}),
                "分割上限": ("INT", {"default": 8, "min": 1, "max": 100, "step": 1}),
            },
            "hidden": {"unique_id": "UNIQUE_ID"},
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("split_text",)
    OUTPUT_IS_LIST = (True,) 
    FUNCTION = "gate_logic"
    CATEGORY = "HuiXin/Utils"

    def gate_logic(self, line_text, 删除空行, 删除首尾空白, 分割上限, unique_id=None):
        # 1. 预处理原始文本
        raw_lines = line_text.split('\n')
        processed = []
        for l in raw_lines:
            if 删除首尾空白: l = l.strip()
            if 删除空行 and not l: continue
            processed.append(l)
        
        suggested_lines = processed[:分割上限]
        
        # 2. 发送给前端显示并进入暂停
        PromptServer.instance.send_sync("huixin_hold_execution", {
            "node_id": unique_id,
            "lines": suggested_lines
        })

        # 3. 初始化等待状态
        event = threading.Event()
        huixin_wait_events[unique_id] = event
        huixin_cancel_flags[unique_id] = False # 重置取消标志
        
        print(f"【汇心分割】节点 {unique_id} 正在原地等待确认或取消...")
        
        # 阻塞执行
        event.wait() 
        
        # 4. 判断是被“确认”唤醒还是被“取消”唤醒
        if huixin_cancel_flags.get(unique_id) is True:
            print(f"【汇心分割】节点 {unique_id} 任务已手动取消。")
            # 清理
            self.cleanup(unique_id)
            # 返回空字符串，配合 api.interrupt() 终止
            return (["任务已取消"],)

        # 5. 确认运行
        final_list = huixin_received_data.get(unique_id, suggested_lines)
        self.cleanup(unique_id)

        return (final_list,)

    def cleanup(self, unique_id):
        if unique_id in huixin_wait_events: del huixin_wait_events[unique_id]
        if unique_id in huixin_received_data: del huixin_received_data[unique_id]
        if unique_id in huixin_cancel_flags: del huixin_cancel_flags[unique_id]

# --- 扩展 API 路由 ---
@PromptServer.instance.routes.post("/huixin/resume")
async def resume_node(request):
    json_data = await request.json()
    node_id = json_data.get("node_id")
    user_data = json_data.get("data")
    is_cancel = json_data.get("is_cancel", False)
    
    if node_id in huixin_wait_events:
        if is_cancel:
            huixin_cancel_flags[node_id] = True
        else:
            huixin_received_data[node_id] = user_data
        
        huixin_wait_events[node_id].set() # 唤醒 Python 线程
        return web.json_response({"status": "success"})
    return web.json_response({"status": "error"}, status=404)