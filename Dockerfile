# 多阶段构建：先构建前端，再构建完整镜像
FROM node:20 as frontend-builder

WORKDIR /build/frontend

# 复制前端依赖文件
COPY app/my_analysis_app/package*.json ./

# 安装前端依赖
RUN npm install

# 复制前端源代码
COPY app/my_analysis_app/ ./

# 构建前端
RUN npm run build


# ============================================
# Python 后端 + Nginx 前端 + 模型的最终镜像
# ============================================
FROM python:3.10-slim

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    nginx \
    curl \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    git \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制 QD 模型目录（这是最大的部分）
COPY QD/ /app/QD/

# 复制前端构建结果
COPY --from=frontend-builder /build/frontend/dist /app/frontend/dist

# 复制后端代码
COPY app/my_analysis_app/backend /app/backend

# 安装 Python 依赖
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# 配置 Nginx
RUN rm /etc/nginx/sites-enabled/default

COPY nginx.conf /etc/nginx/sites-enabled/default

# 创建上传目录
RUN mkdir -p /app/backend/uploads

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV PORT=5001
ENV FLASK_APP=/app/backend/app.py

# 暴露端口
EXPOSE 80 5001

# 启动脚本
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
