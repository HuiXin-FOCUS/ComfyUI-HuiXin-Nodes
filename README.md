\# ComfyUI-HuiXin-Nodes (汇心工具箱)



\[English](#english) | \[中文](#chinese)



---



<a name="english"></a>

\## English Description



A comprehensive suite of ComfyUI nodes designed for E-commerce design, image processing, and multi-modal LLM assistance. This toolkit simplifies complex workflows for product photography refinement, detail page creation, and prompt management.



\### 🌟 Key Features

\- \*\*LLM Vision \& Prompts\*\*: Multi-channel LLM support (Grsai, ModelScope, Allapi) for image-to-text and prompt engineering.

\- \*\*E-commerce Optimization\*\*: Specialized nodes for "Detail Page Presets" and "Smart Collage" tailored for platforms like Amazon and Taobao.

\- \*\*Image Utilities\*\*: Advanced square cropping by mask, image labeling, and high-performance image loading.

\- \*\*NanoBananaPro\*\*: High-concurrency AI image generation and refinement with character and style consistency.

\- \*\*Workflow Control\*\*: Prompt splitter with "Hold \& Resume" capability for manual intervention.



\### 🛠 Installation

1\. Navigate to your `ComfyUI/custom\_nodes` folder.

2\. Clone this repository:

&nbsp;  ```bash

&nbsp;  git clone https://github.com/HuiXin-FOCUS/ComfyUI-HuiXin-Nodes.git

Install dependencies:

code

Bash

pip install -r requirements.txt

Restart ComfyUI.

<a name="chinese"></a>

中文说明

汇心工具箱 是一套专为电商设计、图像处理和多模态大模型辅助而设计的 ComfyUI 插件包。它简化了产品精修、详情页制作及提示词管理等复杂工作流。

🌟 核心功能

多模态 LLM 反推: 支持多个 API 渠道（Grsai、魔搭、云雾），实现精准的图生文和提示词架构。

电商详情页优化: 内置亚马逊 A+、淘宝主图/详情页预设逻辑，支持智能拼图（瀑布流布局）。

图像处理工具: 提供基于遮罩的方形裁剪、自动标签条生成、高性能图像加载等实用功能。

NanoBananaPro: 支持高并发 AI 图像生成与精修，具备角色一致性与画质增强能力。

工作流控制: 独特的提示词分割节点，支持在运行中暂停并等待人工确认。

🛠 安装方法

进入你的 ComfyUI/custom\_nodes 目录。

克隆本仓库：

code

Bash

git clone https://github.com/HuiXin-FOCUS/ComfyUI-HuiXin-Nodes.git

安装必要依赖：

code

Bash

pip install -r requirements.txt

重启 ComfyUI。

📦 Node List / 节点列表

Category	Node Name	Description (CN)

LLM	HuiXin\_Vision\_LLM	汇心多模态LLM反推

Image	HuiXin\_Smart\_Collage	汇心智能拼图 (支持瀑布流)

Image	HuiXin\_Square\_Crop	汇心方形裁剪 (基于遮罩)

Gen	HuiXin\_NanoBananaPro	汇心 NanoBananaPro 图像生成

Utils	HuiXin\_Prompt\_Library	汇心提示词库 (可视化管理)

Utils	HuiXin\_Prompt\_Splitter	汇心提示词分割 (人工确认)
