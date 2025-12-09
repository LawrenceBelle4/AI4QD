# QD-SAM Docker Build 指南

## 📦 快速开始

### 本地构建和测试

```bash
# 1. 构建镜像
cd /Users/yuzhuolin/Desktop/前端/12_7
docker build -t qd-sam:latest .

# 2. 运行容器
docker run -d \
  --name qd-sam-app \
  -p 80:80 \
  -p 5001:5001 \
  -v $(pwd)/backend_uploads:/app/backend/uploads \
  qd-sam:latest

# 3. 检查是否运行正常
curl http://localhost/health
```

### 使用 Docker Compose（推荐）

```bash
# 1. 启动
docker-compose up -d

# 2. 查看日志
docker-compose logs -f

# 3. 停止
docker-compose down
```

## 🚀 服务器部署

### 前置要求
- Docker 20.10+
- Docker Compose 2.0+
- 至少 16GB RAM
- 至少 50GB 磁盘空间（模型文件很大）

### 步骤 1: 上传文件到服务器

```bash
scp -r /Users/yuzhuolin/Desktop/前端/12_7 user@server:/path/to/deployment
```

### 步骤 2: 在服务器上构建和启动

```bash
ssh user@server

cd /path/to/deployment/12_7

# 构建镜像
docker build -t qd-sam:latest .

# 启动服务
docker-compose up -d
```

### 步骤 3: 验证服务

```bash
# 查看容器状态
docker ps | grep qd-sam

# 测试健康检查
curl http://server_ip/health

# 查看日志
docker-compose logs -f qd-sam-app
```

## 📊 镜像信息

- **基础镜像**: python:3.10-slim + nginx
- **前端**: Vue 3 + Vite（静态构建）
- **后端**: Flask + Python 3.10
- **模型**: SAM2（位于 /app/QD/）
- **暴露端口**: 
  - 80: Nginx 前端
  - 5001: Flask 后端 API

## 🔧 镜像大小估计

- Python 基础镜像: ~150MB
- 前端构建: ~2MB
- 后端依赖: ~500MB
- 模型文件: ~1.2GB
- **总计**: ~1.8GB

## 💾 生产环境建议

### 1. 使用 .dockerignore 减小镜像大小

创建 `.dockerignore`:
```
node_modules/
.git/
.env
.env.local
*.pptx
.DS_Store
```

### 2. 使用私有仓库（如需要）

```bash
# 登录 Docker Registry
docker login registry.example.com

# 标签镜像
docker tag qd-sam:latest registry.example.com/qd-sam:latest

# 推送
docker push registry.example.com/qd-sam:latest

# 在服务器拉取
docker pull registry.example.com/qd-sam:latest
```

### 3. 监控和日志

```bash
# 查看实时日志
docker-compose logs -f

# 导出日志
docker-compose logs > deployment.log

# 检查资源使用
docker stats qd-sam-app
```

### 4. 数据持久化

Docker Compose 已配置以下卷：
- `./backend_uploads`: 上传的文件
- `./nginx_logs`: Nginx 日志

这些数据会在容器重启时保留。

## 🐛 故障排查

### 容器无法启动

```bash
# 查看错误日志
docker logs qd-sam-app

# 检查构建过程
docker build --progress=plain -t qd-sam:latest .
```

### 模型加载失败

```bash
# 验证模型文件在容器内存在
docker exec qd-sam-app ls -la /app/QD/checkpoint/

# 检查 Python 依赖
docker exec qd-sam-app pip list | grep torch
```

### 内存不足

```bash
# 限制容器内存
docker-compose.yml 中添加:
services:
  qd-sam-app:
    deploy:
      resources:
        limits:
          memory: 8G
        reservations:
          memory: 4G
```

## 🔒 安全建议

1. **不要在 Dockerfile 中包含敏感信息**（已遵循）
2. **使用 .dockerignore 排除不必要文件**
3. **定期更新基础镜像**
4. **在生产环境使用反向代理**（已用 Nginx）
5. **配置 CORS 和速率限制**

## 📈 扩展性

### 水平扩展（多个实例）

```bash
# 使用 docker-compose scale
docker-compose up -d --scale qd-sam-app=3
```

### 使用 Kubernetes

对于大规模部署，建议迁移到 Kubernetes。

## 📝 更新镜像

当代码更新时：

```bash
# 重新构建
docker-compose down
docker-compose up -d --build

# 或使用脚本
docker-compose up -d --build --force-recreate
```
