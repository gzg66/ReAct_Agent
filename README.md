# ReAct Agent

这是一个基于 ReAct (Reasoning and Acting) 模式实现的智能 Agent 项目。它利用大语言模型 (LLM) 进行推理，能够动态生成并执行 Python 代码来解决用户问题，甚至执行本地系统操作（如控制鼠标、键盘、文件操作等）。

## 📁 项目结构

```
d:\workspace\work\ReAct_Agent\
├── agent.py         # 核心入口。包含 ReActAgent (主逻辑), CoderAgent (代码生成), CodeExecutor (代码执行)
├── config.py        # 配置文件。设置 API Key 和模型参数
├── init_model.py    # 模型初始化。配置 LangChain 的 ChatOpenAI 和 Embeddings
├── propmts.py       # 提示词管理。包含 Agent 和 Coder 的 System Prompts
└── __pycache__/     # Python 缓存目录
```

## 🚀 快速开始

### 1. 环境准备

确保已安装 Python 3.8+。

安装必要的依赖库：

```bash
pip install langchain langchain-openai langchain-community dashscope
# 如果需要执行系统控制类任务，可能还需要安装:
# pip install pyautogui
```

### 2. 配置 API Key

本项目默认使用阿里云 DashScope (通义千问) 模型。

请在系统环境变量中设置 `DASHSCOPE_API_KEY`，或者直接修改 `config.py` 文件（不推荐直接提交 Key 到代码仓库）：

```python
# config.py
import os
# API_KEY = "sk-xxxxxxxxxxxxxxxx"  # 直接硬编码 (仅本地测试)
API_KEY = os.getenv("DASHSCOPE_API_KEY") # 推荐方式
```

### 3. 运行项目

直接运行 `agent.py` 启动 Agent：

```bash
python agent.py
```

默认的测试任务在 `agent.py` 的 `main` 函数中定义：
```python
query = "打开mumu模拟器，并运行其中的蔚蓝星球游戏" 
```
你可以修改此 `query` 变量来测试不同的指令。

## ⚙️ 核心功能

*   **ReAct 循环**: Agent 遵循 `Thought` -> `Action` -> `Observation` 的循环来逐步解决问题。
*   **代码生成 (CoderAgent)**: 当需要计算、逻辑处理或系统操作时，Agent 会指示 CoderAgent 编写 Python 代码。
*   **代码执行 (CodeExecutor)**: 自动执行生成的代码并捕获标准输出 (`stdout`) 作为观察结果返回给 Agent。
*   **上下文保持**: 整个对话历史会被保留，确保 Agent 能根据之前的步骤进行调整。

## 📝 待办事项 (TODO) & 后续开发计划

为了完善此项目，可以在以下方面进行迭代：

1.  **安全性增强**: 
    *   目前 `exec()` 拥有较高权限。建议引入沙箱机制 (Sandbox) 或 Docker 容器来执行生成的代码，防止误操作本地文件。
    *   限制可导入的库白名单。

2.  **工具库扩展**:
    *   目前主要依赖动态生成代码 (`CREATE_TOOL`)。可以预定义一些常用工具 (如 `GoogleSearch`, `FileRead`) 供 Agent 直接调用，减少代码生成的不确定性。

3.  **交互优化**:
    *   将 `print` 输出改为日志系统 (`logging`)。
    *   开发 Web UI (Streamlit/Gradio) 替代命令行交互。

4.  **记忆机制**:
    *   引入长期记忆 (Vector Store) 来存储过往的任务经验。

5.  **模型适配**:
    *   在 `config.py` 中增加对其他模型厂商 (OpenAI, DeepSeek 等) 的支持配置。

## ⚠️ 注意事项

*   **高危权限**: 由于 Agent 具有 `exec` 权限且被告知“拥有最高的系统操作权限”，请务必在受控环境中运行，避免让其执行删除文件等危险操作。
*   **JSON 解析**: 依赖 LLM 返回严格的 JSON 格式，偶尔可能会因模型输出格式错误导致解析失败（代码中已包含重试机制）。
