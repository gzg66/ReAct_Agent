import json
import io
import contextlib
import traceback
import sys

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# 假设这些文件都在同一级目录下
import config
import init_model
import propmts

class CodeExecutor:
    """
    工具组件：负责执行 Python 代码并捕获输出
    """
    @staticmethod
    def execute(code_str):
        print(f"   [System] 正在执行生成的代码...")
        
        # 捕获标准输出
        output_capture = io.StringIO()
        try:
            # 使用 contextlib 捕获 print 的输出
            with contextlib.redirect_stdout(output_capture):
                # -----------------------------------------------------------
                # 关键修复：使用单一字典作为 globals 和 locals
                # 这确保了顶层的 import 对函数内部可见
                # -----------------------------------------------------------
                execution_scope = {
                    "__builtins__": __builtins__,
                    "math": __import__("math"),
                    "json": __import__("json")
                }
                
                # 执行代码 (将 execution_scope 既作为 globals 也作为 locals)
                exec(code_str, execution_scope)
                
            result = output_capture.getvalue().strip()
            
            if not result:
                return "代码执行成功，但没有产生任何输出 (stdout为空)。请确保代码最后调用了函数并使用了 print() 打印结果。"
                
            return result
            
        except ImportError as e:
             return f"执行错误: 缺少必要的库。Agent 尝试导入了一个未安装的库。"
        except Exception as e:
            # 捕获运行时错误
            error_msg = f"Runtime Error: {str(e)}\n{traceback.format_exc()}"
            return error_msg

class CoderAgent:
    """
    子代理：专门负责编写代码
    """
    def __init__(self):
        # 复用 init_model 中定义的 LLM
        self.llm = init_model.Text_llm
        self.system_prompt = propmts.CODER_SYSTEM_PROMPT

    def generate_code(self, requirement):
        """
        根据需求生成 Python 代码
        """
        print(f"   [Coder] 正在编写代码: {requirement} ...")
        
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"需求：{requirement}")
        ]
        
        response = self.llm.invoke(messages)
        code_content = response.content
        
        # 清洗代码：去除可能存在的 Markdown 标记 (```python ... ```)
        clean_code = code_content
        if "```python" in code_content:
            clean_code = code_content.split("```python")[1].split("```")[0]
        elif "```" in code_content:
            clean_code = code_content.split("```")[1].split("```")[0]
            
        return clean_code.strip()

class ReActAgent:
    """
    主代理：负责推理、决策和协调
    """
    def __init__(self):
        self.llm = init_model.Text_llm
        self.coder = CoderAgent()
        self.executor = CodeExecutor()
        self.max_steps = 8 # 最大思考步数
        self.history = []  # 存储对话历史 (LangChain Messages)

    def run(self, user_query):
        print(f"\n=== 开始新任务: {user_query} ===")
        
        # 1. 初始化对话历史
        self.history = [
            SystemMessage(content=propmts.AGENT_SYSTEM_PROMPT),
            HumanMessage(content=user_query)
        ]
        
        step = 0
        while True:
            step += 1
            print(f"\n>> Step {step}")
            
            # 2. 调用 LLM 获取思考和行动
            try:
                response = self.llm.invoke(self.history)
                response_text = response.content
                
                # 打印原始思考 (用于调试)
                print(f"\033[94m[Agent Response]\n{response_text}\033[0m") 
                
                # 将 Agent 的回复加入历史，保持上下文
                self.history.append(AIMessage(content=response_text))
                
            except Exception as e:
                print(f"LLM 调用失败: {e}")
                return
            
            # 3. 解析 JSON (增强鲁棒性)
            try:
                # 提取 JSON 字符串（防止模型在 JSON 前后输出废话）
                json_str = response_text
                if "{" in response_text and "}" in response_text:
                    start = response_text.find("{")
                    end = response_text.rfind("}") + 1
                    json_str = response_text[start:end]
                
                decision = json.loads(json_str)
            except json.JSONDecodeError:
                print("解析 JSON 失败，要求 Agent 重试...")
                self.history.append(HumanMessage(content="系统提示：解析你的响应失败。请务必只返回有效的 JSON 格式数据，不要包含其他文本。"))
                continue

            # 4. 执行决策
            thought = decision.get("thought", "")
            action = decision.get("action", "")
            content = decision.get("content", "")
            
            if action == "FINAL_ANSWER":
                print(f"\n✅ 任务完成: {content}")
                return content
            
            elif action == "CREATE_TOOL":
                # Step A: 让 Coder 写代码
                code = self.coder.generate_code(content)
                print(f"   [Generated Code]\n{code}")
                
                # Step B: 执行代码
                exec_result = self.executor.execute(code)
                print(f"\033[92m   [Execution Output] {exec_result}\033[0m")
                
                # Step C: 将结果作为 Observation 反馈给 Agent
                observation = f"Observation: 代码执行结果如下：\n{exec_result}\n请根据此结果进行分析或给出最终答案。"
                self.history.append(HumanMessage(content=observation))
            
            else:
                print(f"未知的动作: {action}")
                # 反馈错误给 Agent
                self.history.append(HumanMessage(content=f"系统提示：收到未知的 action '{action}'。支持的 action 只有 'CREATE_TOOL' 和 'FINAL_ANSWER'。"))


def main():
    print("-" * 100)

    agent = ReActAgent()
    
    # 你可以修改这里的测试问题
    query = "打开mumu模拟器，并运行其中的蔚蓝星球游戏" 
    
    agent.run(query)

if __name__ == "__main__":
    main()