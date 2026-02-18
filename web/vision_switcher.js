import { app } from "../../scripts/app.js";

// 必须和 __init__.py 中的 Key 一致
const TARGET_NODE = "HuiXin_Vision_LLM"; 

const DB = {
    "Grsai": [
        "gemini-2.5-flash", 
        "gemini-2.5-flash-lite", 
        "gemini-2.5-pro", 
        "gemini-3-pro", 
        "nano-banana-fast", 
        "nano-banana", 
        "gpt-4o-mini"
    ],
    "ModelScope (魔搭)": [
        "qwen-vl-max",
        "qwen-vl-plus",
        "qwen-vl-chat-v1"
    ],
    "Allapi (云雾)": [
        "gemini-1.5-pro-latest",
        "gemini-1.5-flash-latest",
        "gpt-4o",
        "gpt-4o-mini",
        "claude-3-5-sonnet-20240620"
    ]
};

app.registerExtension({
    name: "HuiXin.Vision.Switcher",
    
    nodeCreated(node) {
        if (node.comfyClass === TARGET_NODE) {
            console.log(`[汇心JS] 成功捕获节点: ${TARGET_NODE}`);

            const channelWidget = node.widgets.find(w => w.name === "channel");
            const modelWidget = node.widgets.find(w => w.name === "model");

            if (!channelWidget || !modelWidget) return;

            const updateModels = (channelName) => {
                const list = DB[channelName];
                if (list) {
                    modelWidget.options.values = [...list];
                    // 如果当前值不在新列表里，默认选第一个
                    if (!list.includes(modelWidget.value)) {
                        modelWidget.value = list[0];
                    }
                    node.setDirtyCanvas(true, true);
                }
            };

            const oldCb = channelWidget.callback;
            channelWidget.callback = function(val) {
                updateModels(val);
                if (oldCb) oldCb.apply(this, arguments);
            };

            setTimeout(() => {
                updateModels(channelWidget.value);
            }, 100);
        }
    }
});