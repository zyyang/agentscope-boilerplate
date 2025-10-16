#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ReAct Agent Service Main Entry Point."""
import asyncio
import os
from dotenv import load_dotenv

from app.agent_service import ReActAgentService
from app.utils.logging_config import setup_logging


def load_environment():
    """加载环境变量."""
    load_dotenv()
    
    # 检查必要的环境变量
    required_vars = ['DASHSCOPE_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"⚠️  Missing environment variables: {missing_vars}")
        print("Please make sure they are set in your .env file or environment")


async def main():
    """主函数."""
    load_environment()
    setup_logging()
    
    service = ReActAgentService()
    await service.run_service()


def local_deploy():
    """本地部署入口点."""
    asyncio.run(main())


if __name__ == "__main__":
    local_deploy()