# -*- coding: utf-8 -*-
"""ReAct Agent Builder."""
import os
import logging

from agentscope.agent import ReActAgent
from agentscope.formatter import DashScopeChatFormatter
from agentscope.memory import InMemoryMemory
from agentscope.model import DashScopeChatModel
from agentscope.tool import (
    Toolkit,
    execute_shell_command,
    execute_python_code,
    view_text_file,
)

from agentscope_runtime.engine.agents.agentscope_agent import AgentScopeAgent

logger = logging.getLogger(__name__)


def build_default_agent() -> AgentScopeAgent:
    """构建 ReAct 智能体."""
    # 创建工具包
    toolkit = Toolkit()
    toolkit.register_tool_function(execute_shell_command)
    toolkit.register_tool_function(execute_python_code)
    toolkit.register_tool_function(view_text_file)

    # 系统提示词
    sys_prompt = """你是一个名叫Friday的有用助手。
请直接、简洁地回答用户的问题，不要重复相同的内容。
如果用户的问题需要多步思考，请在思考过程中保持简洁。"""

    # 创建 AgentScope 智能体
    agent = AgentScopeAgent(
        name="Friday",
        model=DashScopeChatModel(
            model_name=os.getenv("MODEL_NAME", "qwen-max"),
            api_key=os.getenv("DASHSCOPE_API_KEY"),
        ),
        agent_config={
            "sys_prompt": sys_prompt,
            # "formatter": DashScopeChatFormatter(),
            # "toolkit": toolkit,
            # "memory": InMemoryMemory(),
            # "max_react_loop": 3
        },
        agent_builder=ReActAgent,
    )

    return agent