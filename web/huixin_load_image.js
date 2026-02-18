import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "HuiXin.LoadImage",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "HuiXin_Load_Image") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                const r = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;
                const node = this;

                // 只有没有按钮时才添加，防止重复
                if (!node.widgets.find(w => w.name === "清除图片")) {
                    node.addWidget("button", "清除图片", null, () => {
                        // 1. 清空路径值
                        const imageWidget = node.widgets.find(w => w.name === "image");
                        if (imageWidget) {
                            imageWidget.value = "";
                            if (imageWidget.callback) imageWidget.callback("");
                        }

                        // 2. 清除所有图片数据引用
                        node.imgs = null;
                        node.image = null;
                        node.images = null;

                        // 3. 核心：不删除控件，只是把预览图控件“藏起来”
                        if (node.widgets) {
                            node.widgets.forEach(w => {
                                // ComfyUI 内部生成的预览图 widget 类型是 "image"
                                if (w.type === "image") {
                                    w.value = null; // 清空图
                                    w.type = "hidden"; // 将类型改为 hidden，渲染器会自动跳过它
                                }
                            });
                        }

                        // 4. 强制重置高度到初始状态（约120像素）
                        node.size[1] = 120;
                        
                        // 5. 告诉系统：数据变了，但不要立即重绘，等下一帧
                        node.setDirtyCanvas(true, false);
                    });
                }
                return r;
            };
        }
    },
});