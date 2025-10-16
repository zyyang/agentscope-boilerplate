# -*- coding: utf-8 -*-
"""ReAct Agent Service with AgentScope Runtime."""
import asyncio
import os
import signal
import logging
from contextlib import asynccontextmanager

import agentscope

from agentscope_runtime.engine import Runner, LocalDeployManager
from agentscope_runtime.engine.services.context_manager import ContextManager
from agentscope_runtime.engine.services.session_history_service import (
    InMemorySessionHistoryService,
)

from app.agents import build_default_agent

logger = logging.getLogger(__name__)


class ReActAgentService:
    """ReAct Agent 服务类."""
    
    def __init__(self):
        self.runner = None
        self.deploy_manager = None
        self._shutdown_event = asyncio.Event()
        
        # 注册信号处理
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """处理关闭信号."""
        logger.info(f"收到关闭信号 {signum}, 正在关闭服务...")
        self._shutdown_event.set()

    def _initialize_agentscope(self):
        """初始化 AgentScope."""
        # 准备初始化参数
        init_kwargs = {
            "project": os.getenv("PROJECT_NAME", "react-agent-chat")
        }
        
        # 只有在 STUDIO_URL 存在时才添加
        studio_url = os.getenv("STUDIO_URL")
        if studio_url:
            init_kwargs["studio_url"] = studio_url
            logger.info(f"✅ 启用 Studio 监控: {studio_url}")
        else:
            logger.info("ℹ️  Studio URL 未设置，禁用监控功能")

        # 初始化 AgentScope
        agentscope.init(**init_kwargs)

    def _build_agent(self):
        """构建 AgentScope 智能体."""
        try:
            self._initialize_agentscope()
            agent = build_default_agent()
            logger.info("✅ AgentScope agent created successfully")
            return agent
        except Exception as e:
            logger.error(f"❌ Failed to build agent: {e}")
            raise

    @asynccontextmanager
    async def create_runner(self):
        """创建并管理 Runner 的生命周期."""
        try:
            context_manager = ContextManager(
                session_history_service=InMemorySessionHistoryService(),
            )
            
            async with Runner(
                agent=self._build_agent(),
                context_manager=context_manager,
            ) as runner:
                self.runner = runner
                logger.info("✅ Runner created successfully")
                yield runner
                
        except Exception as e:
            logger.error(f"❌ Failed to create runner: {e}")
            raise
        finally:
            self.runner = None

    async def deploy_agent(self, runner: Runner) -> LocalDeployManager:
        """部署智能体服务."""
        try:
            server_port = int(os.getenv("AGENT_PORT", "8080"))
            server_endpoint = os.getenv("AGENT_ENDPOINT", "process")
            host = os.getenv("AGENT_HOST", "localhost")

            deploy_manager = LocalDeployManager(host=host, port=server_port)

            deployment_info = await runner.deploy(
                deploy_manager,
                endpoint_path=f"/{server_endpoint}",
                stream=True,  # Enable streaming responses
            )

            self.deploy_manager = deploy_manager

            logger.info(f"🚀 Agent deployed at: {deployment_info['url']}")
            logger.info(f"🌐 Service URL: {deployment_info['url']}/{server_endpoint}")
            logger.info(f"💚 Health check: {deployment_info['url']}/health")
            
            return deploy_manager

        except Exception as e:
            logger.error(f"❌ Failed to deploy agent: {e}")
            raise

    async def run_service(self):
        """运行智能体服务."""
        try:
            async with self.create_runner() as runner:
                await self.deploy_agent(runner)
                
                logger.info("✅ Service is running. Press Ctrl+C to stop.")
                
                # 等待关闭信号
                while not self._shutdown_event.is_set():
                    await asyncio.sleep(0.1)
                    
        except Exception as e:
            logger.error(f"❌ Service error: {e}")
        finally:
            await self.cleanup()

    async def cleanup(self):
        """清理资源."""
        try:
            if self.deploy_manager and hasattr(self.deploy_manager, 'is_running'):
                if self.deploy_manager.is_running:
                    await self.deploy_manager.stop()
                    logger.info("✅ Service stopped gracefully")
            
            self.deploy_manager = None
            self.runner = None
            
        except Exception as e:
            logger.error(f"❌ Error during cleanup: {e}")