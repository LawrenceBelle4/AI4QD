# 后端 (Flask) 使用说明

这是一个简单的 Flask 后端示例，用于接收图片上传并调用模型（当前为占位实现）。

运行（建议在虚拟环境中执行）：

```bash
cd /Users/yuzhuolin/Desktop/前端/12_7/app/my_analysis_app/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

API:
- `GET /health` 返回健康状态
- `POST /upload` 上传图片，表单字段名为 `file`，返回 JSON 结果

示例 curl:

```bash
curl -F "file=@/path/to/image.jpg" http://localhost:5000/upload
```

将来集成真实模型：替换 `model.py` 中 `predict` 的实现，或把模型加载逻辑改为应用启动时加载以减少每次请求开销。
