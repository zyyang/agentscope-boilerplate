FROM python:3.11-slim

WORKDIR /app

COPY deployments/sources.list /etc/apt/sources.list

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*


RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple
RUN pip install --no-cache-dir --upgrade pip

# 复制依赖文件并安装
COPY --chown=agentuser:agentuser requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# 复制应用代码
COPY . .

# 创建非 root 用户并切换（增强安全）
RUN useradd -m -r agentuser && chown -R agentuser:agentuser /app

USER agentuser

EXPOSE 8080

# 设置健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

CMD ["python", "-m", "app.main"]