#!/bin/bash

# QD-SAM 服务器部署脚本

set -e

echo "========================================="
echo "QD-SAM 一键部署脚本"
echo "========================================="
echo ""

# 配置
REMOTE_USER="${1:-root}"
REMOTE_HOST="${2:-localhost}"
REMOTE_PATH="${3:-/opt/qd-sam}"
LOCAL_PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "📋 部署配置:"
echo "   用户: $REMOTE_USER"
echo "   主机: $REMOTE_HOST"
echo "   远程路径: $REMOTE_PATH"
echo "   本地项目: $LOCAL_PROJECT_DIR"
echo ""

read -p "确认部署信息无误？(y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "已取消"
    exit 1
fi

echo ""
echo "🚀 开始部署..."
echo ""

# 1. 检查远程连接
echo "1️⃣  测试 SSH 连接..."
ssh "$REMOTE_USER@$REMOTE_HOST" "echo '✅ SSH 连接成功'" || {
    echo "❌ 无法连接到 $REMOTE_USER@$REMOTE_HOST"
    exit 1
}

# 2. 创建远程目录
echo ""
echo "2️⃣  准备远程目录..."
ssh "$REMOTE_USER@$REMOTE_HOST" "mkdir -p $REMOTE_PATH && echo '✅ 目录创建完成'"

# 3. 上传文件（显示进度）
echo ""
echo "3️⃣  上传项目文件..."
echo "   (这可能需要几分钟，取决于网络和文件大小)"

rsync -avz \
    --exclude='.git' \
    --exclude='node_modules' \
    --exclude='.DS_Store' \
    --exclude='*.pptx' \
    --exclude='frontend_dist' \
    "$LOCAL_PROJECT_DIR/" \
    "$REMOTE_USER@$REMOTE_HOST:$REMOTE_PATH/"

echo "✅ 文件上传完成"

# 4. 在服务器上构建
echo ""
echo "4️⃣  在服务器上构建 Docker 镜像..."
echo "   (这可能需要 10-20 分钟)"

ssh "$REMOTE_USER@$REMOTE_HOST" << EOF
set -e
cd $REMOTE_PATH

echo "🔨 构建镜像..."
docker build -t qd-sam:latest .

echo "✅ 镜像构建完成"

# 检查旧容器并停止
if docker ps -a --format '{{.Names}}' | grep -q '^qd-sam-app\$'; then
    echo "🛑 停止旧容器..."
    docker-compose down 2>/dev/null || true
fi

echo "✅ 旧容器已清理"
EOF

# 5. 启动容器
echo ""
echo "5️⃣  启动容器..."

ssh "$REMOTE_USER@$REMOTE_HOST" << EOF
cd $REMOTE_PATH

echo "▶️  启动 Docker Compose..."
docker-compose up -d

echo "⏳ 等待服务启动..."
sleep 10

echo "✅ 容器已启动"

# 健康检查
echo ""
echo "🏥 健康检查..."
for i in {1..5}; do
    if curl -s http://localhost/health > /dev/null; then
        echo "✅ 服务健康"
        break
    else
        echo "⏳ 等待服务响应... ($i/5)"
        sleep 3
    fi
done
EOF

# 6. 显示访问信息
echo ""
echo "========================================="
echo "✅ 部署完成！"
echo "========================================="
echo ""
echo "🌐 访问方式:"
echo "   前端: http://$REMOTE_HOST"
echo "   后端 API: http://$REMOTE_HOST:5001"
echo ""
echo "📋 常用命令:"
echo "   查看日志: ssh $REMOTE_USER@$REMOTE_HOST 'cd $REMOTE_PATH && docker-compose logs -f'"
echo "   停止服务: ssh $REMOTE_USER@$REMOTE_HOST 'cd $REMOTE_PATH && docker-compose down'"
echo "   重启服务: ssh $REMOTE_USER@$REMOTE_HOST 'cd $REMOTE_PATH && docker-compose restart'"
echo ""
echo "========================================="
