import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

// 常量定义
const COMFY_COLORS = [
    { name: "Red", value: "#702323" },
    { name: "Brown", value: "#5c3f29" },
    { name: "Green", value: "#285928" },
    { name: "Blue", value: "#232370" },
    { name: "Pale Blue", value: "#3c586b" },
    { name: "Cyan", value: "#236e6e" },
    { name: "Purple", value: "#562370" },
    { name: "Yellow", value: "#706323" },
    { name: "Black", value: "#111111" }
];

// 注入样式
const style = document.createElement("style");
style.textContent = `
    .hx-root { display: flex; flex-direction: column; height: 100%; font-family: Arial, sans-serif; color: white; box-sizing: border-box; }
    .hx-nav { display: flex; gap: 5px; overflow-x: auto; padding: 5px 0; border-bottom: 2px solid #555; margin-bottom: 5px; scrollbar-width: thin; min-height: 30px; }
    .hx-nav::-webkit-scrollbar { height: 4px; }
    .hx-nav-item { background: #222; border: 1px solid #444; border-radius: 15px; padding: 4px 12px; font-size: 12px; cursor: pointer; white-space: nowrap; transition: all 0.2s; user-select: none; }
    .hx-nav-item:hover { background: #444; }
    .hx-nav-item.active { background: #eee; color: #000; font-weight: bold; border-color: #fff; }
    .hx-body { display: flex; flex: 1; overflow: hidden; gap: 5px; }
    .hx-grid { flex: 1; display: flex; flex-wrap: wrap; align-content: flex-start; gap: 6px; overflow-y: auto; padding: 5px; background: rgba(0,0,0,0.2); border-radius: 4px; padding-right: 2px; }
    .hx-grid::-webkit-scrollbar { width: 8px; }
    .hx-grid::-webkit-scrollbar-track { background: rgba(0,0,0,0.1); border-radius: 4px; }
    .hx-grid::-webkit-scrollbar-thumb { background: #555; border-radius: 4px; border: none; }
    .hx-grid::-webkit-scrollbar-thumb:hover { background: #777; }
    .hx-chip { padding: 6px 10px; border-radius: 20px; font-size: 12px; cursor: pointer; max-width: 100%; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; border: 2px solid transparent; opacity: 0.9; user-select: none; box-shadow: 0 2px 4px rgba(0,0,0,0.3); transition: transform 0.1s; }
    .hx-chip:hover { opacity: 1; transform: scale(1.02); z-index: 10; }
    .hx-chip.selected { border-color: #fff; box-shadow: 0 0 8px rgba(255,255,255,0.5); transform: scale(1.02); }
    .hx-sidebar { width: 50px; display: flex; flex-direction: column; gap: 8px; align-items: center; padding-top: 5px; }
    .hx-circle-btn { width: 40px; height: 40px; border-radius: 50%; border: none; background: #333; color: #ddd; font-size: 11px; font-weight: bold; cursor: pointer; display: flex; align-items: center; justify-content: center; box-shadow: 0 2px 5px rgba(0,0,0,0.4); transition: 0.2s; }
    .hx-circle-btn:hover { background: #555; color: #fff; }
    .btn-del { background: #522; border: 1px solid #a44; }
    .btn-del:hover { background: #833; }
    /* pointer-events: none 禁止鼠标与悬浮框交互，防止挡住其他操作 */
    .hx-tooltip { position: fixed; background: #111; color: #eee; padding: 10px 12px; border-radius: 6px; border: 1px solid #444; font-size: 13px; line-height: 1.5; width: 300px; max-height: 400px; overflow-y: auto; white-space: pre-wrap; word-wrap: break-word; z-index: 99999; box-shadow: 0 4px 15px rgba(0,0,0,0.8); display: none; pointer-events: none; }
    .hx-context-menu { position: fixed; background: #222; border: 1px solid #555; box-shadow: 0 5px 15px rgba(0,0,0,0.6); border-radius: 4px; padding: 4px 0; z-index: 99999; min-width: 140px; font-size: 13px; font-family: Arial, sans-serif; }
    .hx-menu-item { display: flex; align-items: center; padding: 6px 12px; cursor: pointer; color: #ccc; transition: background 0.1s; }
    .hx-menu-item:hover { background: #444; color: #fff; }
    .hx-menu-item.danger:hover { background: #a33; }
    .hx-color-swatch { width: 12px; height: 12px; margin-right: 10px; display: inline-block; border: 1px solid rgba(255,255,255,0.2); }
    .hx-menu-divider { height: 1px; background: #444; margin: 4px 0; }
    .hx-modal-mask { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.6); z-index: 10000; display: flex; align-items: center; justify-content: center; }
    .hx-modal { background: #2a2a2a; padding: 20px; border-radius: 12px; width: 350px; box-shadow: 0 10px 30px rgba(0,0,0,0.8); border: 1px solid #444; display: flex; flex-direction: column; gap: 12px; }
    .hx-input, .hx-textarea, .hx-select { background: #111; border: 1px solid #444; color: #eee; padding: 8px; border-radius: 6px; width: 100%; box-sizing: border-box; }
    .hx-textarea { height: 100px; resize: vertical; font-family: monospace; }
    .hx-row { display: flex; gap: 10px; justify-content: space-between; align-items: center; }
    .hx-btn-primary { background: #26a; color: white; padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; }
    .hx-btn-primary:hover { background: #37b; }
    .hx-btn-cancel { background: #444; color: white; padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; }
    .hx-btn-cancel:hover { background: #555; }
`;
document.head.appendChild(style);

// ⚠️ 这里的 Key 必须和 __init__.py 里的 Class Key 一致
const TARGET_NODE = "HuiXin_Prompt_Library";

app.registerExtension({
    name: "Huixin.PromptLibrary",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === TARGET_NODE) {
            
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                if (onNodeCreated) onNodeCreated.apply(this, arguments);

                this.data = { groups: [], prompts: [] };
                this.currentGroup = "全部";
                this.selectedPromptId = null;
                this.tooltipTimer = null;

                const textWidget = this.widgets.find(w => w.name === "text");

                // 创建界面 DOM
                const container = document.createElement("div"); container.className = "hx-root";
                const nav = document.createElement("div"); nav.className = "hx-nav";
                const body = document.createElement("div"); body.className = "hx-body";
                const grid = document.createElement("div"); grid.className = "hx-grid";
                const sidebar = document.createElement("div"); sidebar.className = "hx-sidebar";

                const createBtn = (text, cls, onClick) => {
                    const btn = document.createElement("button");
                    btn.className = `hx-circle-btn ${cls}`;
                    btn.textContent = text;
                    btn.onclick = onClick;
                    return btn;
                };

                sidebar.appendChild(createBtn("改色", "btn-color", (e) => this.actionColor(e.target)));
                sidebar.appendChild(createBtn("编辑", "btn-edit", () => this.actionEdit()));
                sidebar.appendChild(createBtn("添加", "btn-add", () => this.actionAdd(textWidget)));
                sidebar.appendChild(createBtn("删除", "btn-del", () => this.actionDelete()));

                body.append(grid, sidebar); container.append(nav, body);
                
                // 挂载到节点上
                this.addDOMWidget("huixin_ui", "box", container, { serialize: false, hideOnZoom: false });
                this.setSize([550, 400]);
                this.ui = { nav, grid };
                
                // 渲染函数
                this.render = () => {
                    nav.innerHTML = "";
                    const allGroups = ["全部", ...this.data.groups];
                    allGroups.forEach(g => {
                        const item = document.createElement("div");
                        item.className = `hx-nav-item ${this.currentGroup === g ? 'active' : ''}`;
                        item.textContent = g;
                        item.onclick = () => { this.currentGroup = g; this.render(); };
                        item.oncontextmenu = (e) => { e.preventDefault(); this.actionGroupMenu(e, g); };
                        nav.appendChild(item);
                    });

                    grid.innerHTML = "";
                    const filtered = this.currentGroup === "全部" 
                        ? this.data.prompts 
                        : this.data.prompts.filter(p => p.group === this.currentGroup);

                    if (filtered.length === 0) grid.innerHTML = `<div style="color:#777; width:100%; text-align:center; margin-top:20px;">暂无内容</div>`;

                    filtered.forEach(p => {
                        const chip = document.createElement("div");
                        chip.className = `hx-chip ${this.selectedPromptId === p.id ? 'selected' : ''}`;
                        chip.textContent = p.alias || p.text;
                        chip.style.backgroundColor = p.color || "#444";
                        chip.style.color = "#fff"; 
                        chip.onclick = () => {
                            this.selectedPromptId = p.id;
                            textWidget.value = p.text;
                            app.graph.setDirtyCanvas(true, true);
                            this.render();
                        };
                        
                        // 【恢复】这两行代码恢复了，鼠标放在标签（绿色区域）上会显示预览
                        // 因为这里只绑定了 chip (标签)，所以上方的红色文本框不会受影响
                        chip.onmouseenter = (e) => this.showTooltip(e, p.text);
                        chip.onmouseleave = () => this.hideTooltipWithDelay();
                        
                        grid.appendChild(chip);
                    });
                };
                
                // 初始加载数据
                this.loadData();
            };

            // === 方法定义 ===
            
            // 核心功能：右键菜单
            nodeType.prototype.actionGroupMenu = function(e, groupName) {
                if (groupName === "全部") return; 
                const existing = document.getElementById("hx-group-menu");
                if (existing) document.body.removeChild(existing);
                const menu = document.createElement("div"); menu.id = "hx-group-menu"; menu.className = "hx-context-menu";
                const title = document.createElement("div"); title.style.padding = "6px 12px"; title.style.color = "#888"; title.style.borderBottom = "1px solid #444"; title.style.fontSize = "12px"; title.textContent = `分组: ${groupName}`;
                menu.appendChild(title);
                const delItem = document.createElement("div"); delItem.className = "hx-menu-item danger"; delItem.innerHTML = "🗑️ 删除此分组";
                delItem.onclick = () => { this.confirmDeleteGroup(groupName); closeMenu(); };
                menu.appendChild(delItem);
                document.body.appendChild(menu);
                menu.style.left = e.clientX + "px"; menu.style.top = e.clientY + "px";
                const handleOutsideClick = (evt) => { if (!menu.contains(evt.target)) closeMenu(); };
                const closeMenu = () => { if (document.body.contains(menu)) document.body.removeChild(menu); window.removeEventListener("pointerdown", handleOutsideClick, { capture: true }); };
                setTimeout(() => window.addEventListener("pointerdown", handleOutsideClick, { capture: true }), 50);
            };

            // 核心功能：删除分组确认
            nodeType.prototype.confirmDeleteGroup = function(groupName) {
                const count = this.data.prompts.filter(p => p.group === groupName).length;
                const mask = document.createElement("div"); mask.className = "hx-modal-mask";
                mask.innerHTML = `
                    <div class="hx-modal" style="width:300px; text-align:center;">
                        <h3>删除分组: ${groupName}</h3>
                        <p style="color:#ccc; font-size:13px; margin:10px 0;">包含 <b>${count}</b> 个提示词。<br>删除将同时删除这些提示词！</p>
                        <div class="hx-row" style="justify-content:center; gap:10px; margin-top:15px;">
                            <button id="hx-grp-cancel" class="hx-btn-cancel">取消</button>
                            <button id="hx-grp-del" class="hx-btn-primary" style="background:#a33;">确认删除</button>
                        </div>
                    </div>`;
                document.body.appendChild(mask);
                document.getElementById("hx-grp-cancel").onclick = () => document.body.removeChild(mask);
                document.getElementById("hx-grp-del").onclick = () => {
                    this.data.prompts = this.data.prompts.filter(p => p.group !== groupName);
                    this.data.groups = this.data.groups.filter(g => g !== groupName);
                    if (this.currentGroup === groupName) this.currentGroup = "全部";
                    this.saveData();
                    document.body.removeChild(mask);
                };
            };

            // 悬浮提示
            nodeType.prototype.showTooltip = function(e, text) {
                if (this.tooltipTimer) { clearTimeout(this.tooltipTimer); this.tooltipTimer = null; }
                let tooltip = document.getElementById("hx-global-tooltip");
                if (!tooltip) {
                    tooltip = document.createElement("div"); tooltip.id = "hx-global-tooltip"; tooltip.className = "hx-tooltip";
                    document.body.appendChild(tooltip);
                }
                tooltip.textContent = text; tooltip.style.display = "block";
                const rect = e.target.getBoundingClientRect();
                let left = rect.right + 10; let top = rect.top;
                if (left + 310 > window.innerWidth) left = rect.left - 310;
                const h = Math.min(400, tooltip.scrollHeight);
                if (top + h > window.innerHeight) top = window.innerHeight - h - 20;
                tooltip.style.left = left + "px"; tooltip.style.top = top + "px"; tooltip.scrollTop = 0;
            };

            nodeType.prototype.hideTooltipWithDelay = function() {
                if (this.tooltipTimer) clearTimeout(this.tooltipTimer);
                this.tooltipTimer = setTimeout(() => {
                    const tooltip = document.getElementById("hx-global-tooltip"); if (tooltip) tooltip.style.display = "none";
                }, 0); 
            };

            // 操作：添加
            nodeType.prototype.actionAdd = function(textWidget) {
                this.showModal({
                    title: "添加提示词", mode: "add", text: textWidget.value,
                    group: this.currentGroup === "全部" ? (this.data.groups[0] || "默认") : this.currentGroup,
                    color: "#232370", groups: this.data.groups,
                    onSave: (newData) => { this.updateGroupList(newData.group); this.data.prompts.push({ id: Date.now(), ...newData }); this.saveData(); }
                });
            };

            // 操作：编辑
            nodeType.prototype.actionEdit = function() {
                if (!this.selectedPromptId) return alert("请先选择一个提示词！");
                const item = this.data.prompts.find(p => p.id === this.selectedPromptId);
                this.showModal({
                    title: "编辑提示词", mode: "edit", text: item.text, alias: item.alias, group: item.group, color: item.color, groups: this.data.groups,
                    onSave: (newData) => { this.updateGroupList(newData.group); Object.assign(item, newData); this.saveData(); }
                });
            };

            nodeType.prototype.updateGroupList = function(newGroup) {
                if (newGroup && !this.data.groups.includes(newGroup)) this.data.groups.push(newGroup);
            };

            // 弹窗逻辑
            nodeType.prototype.showModal = function(options) {
                const mask = document.createElement("div"); mask.className = "hx-modal-mask";
                const uniqueGroups = [...new Set(options.groups)];
                const groupOptions = uniqueGroups.map(g => `<option value="${g}" ${g === options.group ? 'selected' : ''}>${g}</option>`).join("");
                mask.innerHTML = `
                    <div class="hx-modal">
                        <h3 style="margin:0; color:#ddd;">${options.title}</h3>
                        <div><label style="font-size:12px; color:#888;">别名</label><input class="hx-input" id="hx-alias" value="${options.alias || ''}" placeholder="按钮显示的名称"></div>
                        <div><label style="font-size:12px; color:#888;">内容</label><textarea class="hx-textarea" id="hx-text">${options.text || ''}</textarea></div>
                        <div class="hx-row">
                            <div style="flex:1;">
                                <label style="font-size:12px; color:#888;">分组 (下拉选择 或 新建)</label>
                                <div style="position:relative;">
                                    <select class="hx-select" id="hx-group-select" style="width:100%;">${groupOptions}<option value="__NEW__" style="color:#aaa;">➕ 新建分组...</option></select>
                                    <input class="hx-input" id="hx-group-input" placeholder="输入新分组名称..." style="width:100%; display:none;">
                                </div>
                            </div>
                        </div>
                        <div class="hx-row" style="justify-content:flex-end; margin-top:10px; gap: 8px;">
                            <button id="hx-cancel" class="hx-btn-cancel">取消</button>
                            <button id="hx-save" class="hx-btn-primary">保存</button>
                        </div>
                    </div>
                `;
                document.body.appendChild(mask);
                const selectEl = document.getElementById("hx-group-select");
                const inputEl = document.getElementById("hx-group-input");
                if (options.group && !uniqueGroups.includes(options.group)) { selectEl.style.display = "none"; inputEl.style.display = "block"; inputEl.value = options.group; }
                selectEl.onchange = () => { if (selectEl.value === "__NEW__") { selectEl.style.display = "none"; inputEl.style.display = "block"; inputEl.value = ""; inputEl.focus(); } };
                const handleSave = () => {
                    const text = document.getElementById("hx-text").value;
                    if (!text.trim()) return alert("内容不能为空");
                    let finalGroup = selectEl.value;
                    if (inputEl.style.display !== "none") finalGroup = inputEl.value.trim();
                    options.onSave({ text: text, alias: document.getElementById("hx-alias").value || text.substring(0, 10), group: finalGroup || "默认", color: options.color });
                    document.body.removeChild(mask);
                };
                document.getElementById("hx-cancel").onclick = () => document.body.removeChild(mask);
                document.getElementById("hx-save").onclick = handleSave;
            };

            // 操作：改色
            nodeType.prototype.actionColor = function(btnElement) {
                if (!this.selectedPromptId) return alert("请先选择一个提示词！");
                const existing = document.getElementById("hx-color-menu");
                if (existing) document.body.removeChild(existing);
                const menu = document.createElement("div"); menu.id = "hx-color-menu"; menu.className = "hx-context-menu";
                const apply = (c) => { const item = this.data.prompts.find(p => p.id === this.selectedPromptId); if (item) { item.color = c; this.saveData(); } closeMenu(); };
                COMFY_COLORS.forEach(c => {
                    const item = document.createElement("div"); item.className = "hx-menu-item"; item.innerHTML = `<span class="hx-color-swatch" style="background:${c.value}"></span>${c.name}`;
                    item.onclick = (e) => { e.stopPropagation(); apply(c.value); }; menu.appendChild(item);
                });
                const div = document.createElement("div"); div.className = "hx-menu-divider"; menu.appendChild(div);
                const custom = document.createElement("div"); custom.className = "hx-menu-item"; custom.innerHTML = `<span class="hx-color-swatch" style="background:linear-gradient(135deg,#f0f,#ff0)"></span>Custom...`;
                const picker = document.createElement("input"); picker.type = "color"; picker.style.display = "none"; picker.onchange = (e) => apply(e.target.value); picker.onclick = (e) => e.stopPropagation();
                custom.appendChild(picker); custom.onclick = (e) => { e.stopPropagation(); picker.click(); }; menu.appendChild(custom);
                document.body.appendChild(menu);
                const btnRect = btnElement.getBoundingClientRect(); const menuHeight = menu.offsetHeight; const windowHeight = window.innerHeight;
                let left = btnRect.right + 5; let top = btnRect.top;
                if (top + menuHeight > windowHeight) { top = windowHeight - menuHeight - 10; if (top < 0) top = 10; }
                menu.style.left = left + "px"; menu.style.top = top + "px";
                const handleOutsideClick = (e) => { if (menu.contains(e.target) || e.target === btnElement) return; closeMenu(); };
                const closeMenu = () => { if (document.body.contains(menu)) document.body.removeChild(menu); window.removeEventListener("pointerdown", handleOutsideClick, { capture: true }); };
                setTimeout(() => window.addEventListener("pointerdown", handleOutsideClick, { capture: true }), 50);
            };

            // 操作：删除
            nodeType.prototype.actionDelete = function() {
                if (!this.selectedPromptId) return alert("请先选择一个提示词！");
                const mask = document.createElement("div"); mask.className = "hx-modal-mask";
                mask.innerHTML = `
                    <div class="hx-modal" style="width:250px; text-align:center;">
                        <h3>确认删除?</h3>
                        <div class="hx-row" style="justify-content:center; gap:10px; margin-top:15px;">
                            <button id="hx-del-no" class="hx-btn-cancel">取消</button>
                            <button id="hx-del-yes" class="hx-btn-primary" style="background:#a33;">删除</button>
                        </div>
                    </div>`;
                document.body.appendChild(mask);
                document.getElementById("hx-del-no").onclick = () => document.body.removeChild(mask);
                document.getElementById("hx-del-yes").onclick = () => {
                    this.data.prompts = this.data.prompts.filter(p => p.id !== this.selectedPromptId);
                    this.selectedPromptId = null;
                    this.saveData();
                    document.body.removeChild(mask);
                };
            };

            // 数据存取 (Python 端的接口支持)
            nodeType.prototype.saveData = async function() { await api.fetchApi("/huixin/save", { method: "POST", body: JSON.stringify(this.data) }); this.render(); };
            nodeType.prototype.loadData = async function() {
                const res = await api.fetchApi("/huixin/data");
                if (res.status === 200) { this.data = await res.json(); if(!this.data.groups) this.data.groups = []; if(!this.data.prompts) this.data.prompts = []; this.render(); }
            };
        }
    }
});