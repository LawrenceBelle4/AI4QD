# Docker 部署快速参考

## 📦 本地测试构建

```bash
cd /Users/yuzhuolin/Desktop/前端/12_7

# 方式 1: 使用脚本（推荐）
./build-docker.sh qd-sam:latest

# 方式 2: 直接 Docker 命令
docker build -t qd-sam:latest .
```

## 🚀 本地运行测试

### 使用 Docker Compose（推荐）
```bash
cd /Users/yuzhuolin/Desktop/前端/12_7

# 启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止
docker-compose down
```

### 使用 Docker run 命令
```bash
docker run -d \
  --name qd-sam-app \
  -p 80:80 \
  -p 5001:5001 \
  -v $(pwd)/backend_uploads:/app/backend/uploads \
  qd-sam:latest

# 查看日志
docker logs -f qd-sam-app

# 停止
docker stop qd-sam-app
docker rm qd-sam-app
```

## 🌐 访问应用

- **前端**: http://localhost
- **后端 API**: http://localhost:5001
- **健康检查**: http://localhost/health

## 🖥️ 服务器部署（一键部署）

### 前提条件
- 服务器已安装 Docker 和 Docker Compose
- SSH 密钥认证已配置

### 自动部署
```bash
cd /Users/yuzhuolin/Desktop/前端/12_7

# 语法
./deploy-server.sh <ssh_user> <server_ip> <remote_path>

# 示例 1: root 用户
./deploy-server.sh root 192.168.1.100 /opt/qd-sam

# 示例 2: ubuntu 用户
./deploy-server.sh ubuntu 192.168.1.100 /home/ubuntu/qd-sam

# 示例 3: 使用默认值（需手动配置 SSH）
./deploy-server.sh
```

### 手动部署步骤

#### Step 1: 上传文件到服务器
```bash
# 本地
scp -r /Users/yuzhuolin/Desktop/前端/12_7 \
    ubuntu@192.168.1.100:/home/ubuntu/qd-sam
```

#### Step 2: 在服务器上构建和启动
```bash
# SSH 连接服务器
ssh ubuntu@192.168.1.100

# 进入项目目录
cd /home/ubuntu/qd-sam

# 构建镜像
docker build -t qd-sam:latest .

# 启动服务
docker-compose up -d

# 查看日志（实时）
docker-compose logs -f

# 查看状态
docker ps
curl http://localhost/health
```

## 🔧 常用 Docker 命令

| 操作 | 命令 |
|------|------|
| **构建镜像** | `docker build -t qd-sam:latest .` |
| **运行容器** | `docker run -d -p 80:80 qd-sam:latest` |
| **查看镜像** | `docker images` |
| **查看容器** | `docker ps -a` |
| **查看日志** | `docker logs -f <container_id>` |
| **进入容器** | `docker exec -it <container_id> bash` |
| **停止容器** | `docker stop <container_id>` |
| **删除容器** | `docker rm <container_id>` |
| **删除镜像** | `docker rmi qd-sam:latest` |
| **推送镜像** | `docker push registry.example.com/qd-sam:latest` |

## 📊 Docker Compose 常用命令

| 操作 | 命令 |
|------|------|
| **启动服务** | `docker-compose up -d` |
| **查看日志** | `docker-compose logs -f` |
| **停止服务** | `docker-compose down` |
| **重启服务** | `docker-compose restart` |
| **查看状态** | `docker-compose ps` |
| **重新构建** | `docker-compose up -d --build` |
| **查看资源用量** | `docker stats` |

## 📁 文件结构

```
12_7/
├── Dockerfile              # Docker 镜像配置
├── docker-compose.yml      # Docker Compose 配置
├── docker-entrypoint.sh    # 容器启动脚本
├── nginx.conf              # Nginx 反向代理配置
├── .dockerignore           # Docker 构建忽略文件
├── build-docker.sh         # 本地构建脚本
├── deploy-server.sh        # 服务器部署脚本
├── DOCKER_GUIDE.md         # 详细部署指南
├── QD/                     # 模型文件目录
├── app/                    # 前后端应用代码
└── README.md
```

## 🐛 故障排查

### 镜像构建失败
```bash
# 查看构建输出
docker build --progress=plain -t qd-sam:latest .

# 或查看详细错误
docker build --no-cache -t qd-sam:latest .
```

### 容器无法启动
```bash
# 查看容器日志
docker logs qd-sam-app

# 或
docker-compose logs qd-sam-app
```

### 模型加载失败
```bash
# 进入容器检查
docker exec -it qd-sam-app bash

# 检查模型文件
ls -la /app/QD/checkpoint/

# 测试 Python 环境
python3 -c "import torch; print(torch.__version__)"
```

### 磁盘空间不足
```bash
# 清理 Docker 资源
docker system prune -a

# 查看磁盘用量
docker system df
```

## 📈 性能优化

### 使用多层缓存
```bash
# 修改 Dockerfile 顺序，经常变化的内容放在后面
# 这样 Docker 可以复用之前的缓存层
```

### 减小镜像大小
```bash
# 在 Dockerfile 中使用多阶段构建
# 已在 Dockerfile 中实现
```

### 限制容器资源
修改 `docker-compose.yml`:
```yaml
services:
  qd-sam-app:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 8G
        reservations:
          cpus: '1'
          memory: 4G
```

## 🔒 安全建议

1. **使用非 root 用户**（待实现）
2. **定期更新基础镜像**
3. **不要在镜像中存储敏感信息**（已遵循）
4. **使用 .dockerignore 排除不必要文件**（已实现）
5. **在生产环境使用 HTTPS**（需配置）

## 📝 更新和维护

### 代码更新
```bash
# 本地修改代码后
docker-compose down
docker-compose up -d --build
```

### 服务器更新
```bash
ssh user@server
cd /path/to/deployment
git pull  # 如果使用 git
docker-compose down
docker-compose up -d --build
```

---

**最后更新**: 2025-12-09
**维护者**: QD-SAM 开发团队
