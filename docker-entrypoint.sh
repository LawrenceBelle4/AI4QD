#!/bin/bash
set -e

echo "Starting QD-SAM Analysis Server..."
echo "=================================="

# 启动后端 Flask 应用
echo "Starting Flask backend on port $PORT..."
cd /app/backend
python app.py &
BACKEND_PID=$!

# 等待后端启动
sleep 3

# 启动 Nginx（前端）
echo "Starting Nginx..."
nginx -g "daemon off;" &
NGINX_PID=$!

echo "=================================="
echo "✅ Server started successfully!"
echo "   - Frontend: http://localhost"
echo "   - Backend API: http://localhost:5001"
echo "=================================="

# 保持容器运行
wait
