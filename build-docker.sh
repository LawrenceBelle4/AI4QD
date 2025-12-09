#!/bin/bash

# QD-SAM Docker 构建脚本

set -e

echo "========================================="
echo "QD-SAM Docker 镜像构建开始"
echo "========================================="
echo ""

PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
IMAGE_NAME="${1:-qd-sam:latest}"
IMAGE_TAG="${2:-latest}"

echo "📁 项目目录: $PROJECT_DIR"
echo "🏷️  镜像名称: $IMAGE_NAME"
echo ""

# 检查必要文件
echo "✓ 检查必要文件..."
required_files=(
    "Dockerfile"
    "docker-entrypoint.sh"
    "nginx.conf"
    ".dockerignore"
    "QD"
    "app/my_analysis_app/backend"
)

for file in "${required_files[@]}"; do
    if [ ! -e "$PROJECT_DIR/$file" ]; then
        echo "❌ 缺失文件: $file"
        exit 1
    fi
done
echo "✅ 所有必要文件都存在"
echo ""

# 开始构建
echo "🔨 开始构建 Docker 镜像..."
echo "   (这可能需要 5-15 分钟，取决于网络和磁盘速度)"
echo ""

docker build \
    --progress=plain \
    -t "$IMAGE_NAME" \
    -f "$PROJECT_DIR/Dockerfile" \
    "$PROJECT_DIR"

BUILD_EXIT_CODE=$?

echo ""
echo "========================================="

if [ $BUILD_EXIT_CODE -eq 0 ]; then
    echo "✅ 镜像构建成功！"
    echo ""
    echo "📊 镜像信息:"
    docker images | grep "$IMAGE_NAME" | awk '{printf "   名称: %s\n   大小: %s\n", $1":"$2, $7}'
    echo ""
    echo "🚀 启动容器:"
    echo "   docker run -d -p 80:80 -p 5001:5001 \\\\
       -v \$(pwd)/backend_uploads:/app/backend/uploads \\\\
       $IMAGE_NAME"
    echo ""
    echo "📝 或使用 Docker Compose:"
    echo "   cd $PROJECT_DIR && docker-compose up -d"
else
    echo "❌ 镜像构建失败 (exit code: $BUILD_EXIT_CODE)"
    exit 1
fi

echo "========================================="
