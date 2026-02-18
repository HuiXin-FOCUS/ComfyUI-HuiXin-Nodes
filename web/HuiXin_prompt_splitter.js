import { app } from "../../../scripts/app.js";
import { api } from "../../../scripts/api.js";

app.registerExtension({
    name: "HuiXin.PromptSplitter",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "HuiXin_Prompt_Splitter") {
            
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                const r = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;

                // 1. 唯一性保护：如果已经有这个 UI 了，绝对不再创建
                if (this.widgets && this.widgets.find(w => w.name === "_HUIXIN_UI_INTERNAL_")) {
                    return r;
                }

                // 2. 创建 UI 容器
                const mainWrapper = document.createElement("div");
                mainWrapper.style.cssText = `
                    display: flex; flex-direction: column; 
                    background-color: #1a1a1a; border-radius: 6px;
                    border: 1px solid #444; margin: 5px; padding: 8px;
                    box-sizing: border-box;
                `;

                // --- 状态栏 ---
                const statusLine = document.createElement("div");
                statusLine.style.cssText = `font-size: 12px; color: #888; margin-bottom: 8px; display: flex; align-items: center; gap: 5px;`;
                const statusDot = document.createElement("span");
                statusDot.innerText = "●"; statusDot.style.color = "#00ff00";
                const statusText = document.createElement("span");
                statusText.innerText = "准备就绪";
                statusLine.appendChild(statusDot); statusLine.appendChild(statusText);
                mainWrapper.appendChild(statusLine);

                // --- 内容区 ---
                const contentRow = document.createElement("div");
                contentRow.style.cssText = "display: flex; flex-direction: row; gap: 5px; height: 380px;";
                const listContainer = document.createElement("div");
                listContainer.style.cssText = "flex: 1; display: flex; flex-direction: column; gap: 8px; overflow-y: auto; padding-right: 4px;";
                const navBar = document.createElement("div");
                navBar.style.cssText = "width: 28px; display: flex; flex-direction: column; gap: 4px; align-items: center; border-left: 1px solid #333; overflow-y: auto;";
                contentRow.appendChild(listContainer); contentRow.appendChild(navBar);
                mainWrapper.appendChild(contentRow);

                // --- 按钮区 ---
                const btnRow = document.createElement("div");
                btnRow.style.cssText = "display: flex; gap: 8px; margin-top: 10px;";
                const confirmBtn = document.createElement("button");
                confirmBtn.innerText = "继续执行";
                confirmBtn.style.cssText = "flex: 1; padding: 8px; cursor: pointer; border: none; border-radius: 4px; background-color: #2b5797; color: white; font-weight: bold;";
                const cancelBtn = document.createElement("button");
                cancelBtn.innerText = "取消执行";
                cancelBtn.style.cssText = "flex: 1; padding: 8px; cursor: pointer; border: none; border-radius: 4px; background-color: #444; color: white; font-weight: bold;";
                btnRow.appendChild(confirmBtn); btnRow.appendChild(cancelBtn);
                mainWrapper.appendChild(btnRow);

                // --- 【核心修正：彻底屏蔽序列化】 ---
                // 必须在 setTimeout 之后添加，确保所有 Python 定义的参数已经排好队
                setTimeout(() => {
                    const uiWidget = this.addDOMWidget("_HUIXIN_UI_INTERNAL_", "PROMPT_SPLIT_UI", mainWrapper);
                    
                    // 彻底从保存系统中抹除：不保存值，也不在 JSON 中占位
                    uiWidget.serializeValue = () => undefined;
                    if (!uiWidget.options) uiWidget.options = {};
                    uiWidget.options.serialize = false; 
                    
                    // 显式锁定：防止某些插件强行给它赋值
                    Object.defineProperty(uiWidget, 'value', {
                        get() { return undefined; },
                        set(v) { },
                        configurable: true
                    });

                    // 确保它永远被挤在最后一位，不打乱 0, 1, 2 号参数的位置
                    const idx = this.widgets.indexOf(uiWidget);
                    if (idx !== -1 && idx !== this.widgets.length - 1) {
                        this.widgets.splice(idx, 1);
                        this.widgets.push(uiWidget);
                    }
                }, 100);

                // --- 业务交互逻辑 ---
                const onHold = (event) => {
                    if (event.detail.node_id != this.id) return;
                    this.bgcolor = "#443300"; statusDot.style.color = "#ff9900"; statusText.innerText = "等待确认...";
                    const lines = event.detail.lines;
                    listContainer.innerHTML = ""; navBar.innerHTML = "";
                    lines.forEach((line, index) => {
                        const area = document.createElement("textarea");
                        area.value = line; area.className = "huixin-item";
                        area.style.cssText = "width:100%; min-height:80px; background:#222; color:#fff; border:1px solid #444; padding:8px; font-size:12px; border-radius:4px; box-sizing:border-box; resize:vertical; flex-shrink:0;";
                        listContainer.appendChild(area);
                        const navBtn = document.createElement("div");
                        navBtn.innerText = index + 1;
                        navBtn.style.cssText = "width:18px; height:18px; background:#333; color:#777; font-size:10px; display:flex; align-items:center; justify-content:center; border-radius:50%; cursor:pointer;";
                        navBtn.onclick = () => area.scrollIntoView({ behavior: 'smooth', block: 'center' });
                        navBar.appendChild(navBtn);
                    });
                };
                api.addEventListener("huixin_hold_execution", onHold);

                confirmBtn.onclick = async () => {
                    const textareas = listContainer.querySelectorAll(".huixin-item");
                    const data = Array.from(textareas).map(t => t.value);
                    await api.fetchApi("/huixin/resume", { method: "POST", body: JSON.stringify({ node_id: this.id.toString(), data: data, is_cancel: false }) });
                    this.bgcolor = undefined; statusDot.style.color = "#00ff00"; statusText.innerText = "已发送";
                };

                cancelBtn.onclick = async () => {
                    await api.interrupt();
                    await api.fetchApi("/huixin/resume", { method: "POST", body: JSON.stringify({ node_id: this.id.toString(), is_cancel: true }) });
                    this.bgcolor = undefined; statusDot.style.color = "#ff0000"; statusText.innerText = "任务已取消";
                };

                this.size = [530, 560]; 
                return r;
            };

            // --- 兜底修复逻辑 ---
            // 如果因为之前的错误保存导致值变成了 0，这里强制修复回合法值
            const onConfigure = nodeType.prototype.onConfigure;
            nodeType.prototype.onConfigure = function() {
                onConfigure?.apply(this, arguments);
                if (this.widgets) {
                    this.widgets.forEach(w => {
                        if (w.name === "分割上限" && (w.value === 0 || !w.value)) w.value = 8;
                        if (w.name === "删除空行" && w.value === undefined) w.value = true;
                        if (w.name === "删除首尾空白" && w.value === undefined) w.value = true;
                    });
                }
            };
        }
    }
});