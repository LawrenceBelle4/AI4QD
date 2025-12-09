# QD-SAM 量子点智能识别与特性分析系统

一个基于 SAM2（Segment Anything Model 2）的量子点自动检测和特性分析系统，集成了深度学习推理与数据可视化。

## 项目概述

本系统用于：
- 自动检测图像中的量子点（QD）
- 计算量子点相关特征（数量、密度、直径、形状因子）
- 生成掩码、覆盖图和分布直方图
- 提供友好的 Web 界面进行交互式分析

## 系统架构

```
project/
├── app/
│   └── my_analysis_app/
│       ├── frontend/               # Vue 3 前端
│       │   ├── src/
│       │   │   ├── App.vue
│       │   │   ├── components/     # Vue 组件
│       │   │   │   ├── AnalysisLayout.vue
│       │   │   │   ├── AnalysisResults.vue
│       │   │   │   ├── ImageUploader.vue
│       │   │   │   └── ...
│       │   │   ├── assets/         # CSS 和静态资源
│       │   │   └── main.js
│       │   ├── package.json
│       │   ├── vite.config.js
│       │   └── index.html
│       └── backend/                 # Flask 后端
│           ├── app.py              # Flask 应用
│           ├── model.py            # SAM2 模型集成
│           ├── requirements.txt    # Python 依赖
│           └── uploads/            # 上传文件目录
├── 演示/                            # 仓库模型代码和权重
│   ├── configs/                    # SAM2 配置文件
│   ├── checkpoint/                 # 预训练权重
│   ├── train_quantum/              # 量子点训练代码
│   └── ...
└── README.md
```

## 快速开始

### 环境要求
- Python 3.10+
- Node.js 18+
- Git

### 后端设置

```bash
# 创建 Python 虚拟环境
cd app/my_analysis_app/backend
python -m venv venv
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 前端设置

```bash
cd app/my_analysis_app
npm install
```

### 运行系统

**终端 1：启动后端**
```bash
cd app/my_analysis_app/backend
conda activate drawing1  # 或激活你的虚拟环境
PORT=5001 python app.py
```

**终端 2：启动前端**
```bash
cd app/my_analysis_app
npm run dev
```

访问 `http://localhost:5174`（或 Vite 显示的端口）

## 功能特性

### 前端
- ✅ 图片上传界面
- ✅ 加载动画和骨架屏
- ✅ 实时显示处理结果（覆盖图、掩码、直方图）
- ✅ 统计数据显示（数量、密度、直径、方差）
- ✅ 响应式布局

### 后端
- ✅ SAM2 自动掩码生成
- ✅ 掩码后处理（面积过滤、去重）
- ✅ 特征计算（等效直径、形状因子、密度）
- ✅ 可视化生成（PNG 格式）
- ✅ CORS 支持跨域请求

## API 端点

### `/upload` (POST)
上传图片进行分析

**请求：**
```
POST /upload
Content-Type: multipart/form-data

file: <image_file>
```

**响应：**
```json
{
  "filename": "test.jpg",
  "file_url": "/uploads/test.jpg",
  "result": {
    "quantumDotCount": 244,
    "density_per_pixel": 0.00072,
    "average_diameter_px": 21.5,
    "diameter_variance": 4.2,
    "result_image": "test_result_abc123.png",
    "mask_image": "test_mask_abc123.png",
    "histogram_image": "test_hist_abc123.png"
  },
  "images": {
    "result_image_url": "/uploads/test_result_abc123.png",
    "mask_image_url": "/uploads/test_mask_abc123.png",
    "histogram_image_url": "/uploads/test_hist_abc123.png"
  }
}
```

### `/upload-test` (POST)
测试端点，生成虚拟可视化（用于快速测试，无需运行 SAM2 推理）

### `/health` (GET)
健康检查

### `/model/status` (GET)
返回模型加载状态

### `/uploads/<filename>` (GET)
获取上传的文件

## 性能优化建议

### 后端
- 使用 GPU 推理（修改 `model.py` 中的 `device='cuda'`）
- 启用缓存（相同图片快速返回）
- 异步处理长耗时任务

### 前端
- 懒加载大图片
- 虚拟化长列表（如需要）

## 故障排除

### 模型加载失败
- 检查 `演示/` 目录是否包含权重文件
- 验证配置文件路径在 `model.py` 中正确
- 查看后端日志中的详细错误信息

### 前端显示空白
- 确认后端在 `http://localhost:5001` 运行
- 检查浏览器控制台是否有 CORS 错误
- 验证图片 URL 是否正确返回

### 推理缓慢
- SAM2 在 CPU 上推理较慢（可能 1-5 分钟），这是正常的
- 考虑使用 GPU 加速
- 在生产环境中使用专业的推理服务器

## 开发说明

### 修改后端推理逻辑
编辑 `backend/model.py` 中的 `predict()` 函数

### 修改前端 UI
编辑 `src/components/` 中的 Vue 组件

### 添加新的 API 端点
在 `backend/app.py` 中添加新的 `@app.route()` 装饰器函数

## 依赖包

### Python（后端）
- Flask：Web 框架
- flask-cors：跨域支持
- SAM2：自动掩码生成
- PyTorch：深度学习框架
- OpenCV：图像处理
- Pillow：图像 I/O
- NumPy：数值计算
- Matplotlib：图表绘制

### Node.js（前端）
- Vue 3：UI 框架
- Vite：构建工具

详见 `backend/requirements.txt` 和 `package.json`

## 许可证

MIT License

## 作者

Created as QD-SAM Analysis System

## 贡献

欢迎提交 Issue 和 Pull Request！

