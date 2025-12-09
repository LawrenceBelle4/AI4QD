from flask import Flask, request, jsonify, send_from_directory, url_for
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
from model import predict, load_model

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
ALLOWED_EXT = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tif', 'tiff'}

app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 在应用启动时显式加载模型并打印加载结果
model_status = load_model()
print('Model load status:', model_status)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT


@app.route('/health')
def health():
    return jsonify({'status': 'ok'})


@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'no file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'no selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # 构造可访问的文件 URL（通过 /uploads/<filename> 路由）
        try:
            file_url = url_for('uploaded_file', filename=filename, _external=True)
        except Exception:
            # url_for 在某些非请求上下文可能失败，回退为相对路径
            file_url = f'/uploads/{filename}'

        # 调用模型
        try:
            result = predict(file_path)
            
        except Exception as e:
            return jsonify({'error': 'model error', 'details': str(e), 'file_url': file_url}), 500

        # 如果 predict 返回了图片文件名，构建其可访问 URL
        images = {}
        try:
            # 支持返回的字段名：result_image, mask_image, histogram_image
            for key in ('result_image', 'mask_image', 'histogram_image'):
                if key in result and result.get(key):
                    try:
                        images[key + '_url'] = url_for('uploaded_file', filename=result.get(key), _external=True)
                    except Exception:
                        images[key + '_url'] = f"/uploads/{result.get(key)}"
        except Exception:
            images = {}

        response = {'filename': filename, 'file_url': file_url, 'result': result}
        if images:
            response['images'] = images

        return jsonify(response)
    else:
        return jsonify({'error': 'file type not allowed'}), 400


@app.route('/upload-test', methods=['POST'])
def upload_test():
    """快速测试路由：生成虚拟可视化图片进行测试，不实际运行模型推理。"""
    import uuid
    import numpy as np
    import cv2
    
    if 'file' not in request.files:
        return jsonify({'error': 'no file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'no selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        try:
            file_url = url_for('uploaded_file', filename=filename, _external=True)
        except Exception:
            file_url = f'/uploads/{filename}'

        # 生成虚拟可视化图片用于测试
        try:
            base = os.path.splitext(filename)[0]
            suffix = uuid.uuid4().hex[:8]
            
            # 创建虚拟结果图（512x512 蓝色）
            result_img = np.full((512, 512, 3), [255, 0, 0], dtype=np.uint8)
            result_fname = f"{base}_result_{suffix}.png"
            result_path = os.path.join(app.config['UPLOAD_FOLDER'], result_fname)
            cv2.imwrite(result_path, result_img)
            
            # 创建虚拟掩码图（512x512 黑白）
            mask_img = np.random.randint(0, 256, (512, 512), dtype=np.uint8)
            mask_fname = f"{base}_mask_{suffix}.png"
            mask_path = os.path.join(app.config['UPLOAD_FOLDER'], mask_fname)
            cv2.imwrite(mask_path, mask_img)
            
            # 创建虚拟直方图（200x100 白色占位图）
            hist_img = np.full((100, 200, 3), [255, 255, 255], dtype=np.uint8)
            hist_fname = f"{base}_hist_{suffix}.png"
            hist_path = os.path.join(app.config['UPLOAD_FOLDER'], hist_fname)
            cv2.imwrite(hist_path, hist_img)
            
            result = {
                'quantumDotCount': 244,
                'density_per_pixel': 0.00072,
                'average_diameter_px': 21.5,
                'area_mean_px2': 378.1,
                'result_image': result_fname,
                'mask_image': mask_fname,
                'histogram_image': hist_fname,
                'note': 'Test mode: dummy visualization'
            }
            
            # 构建 images 对象
            images = {}
            for key in ('result_image', 'mask_image', 'histogram_image'):
                if key in result and result.get(key):
                    try:
                        images[key + '_url'] = url_for('uploaded_file', filename=result.get(key), _external=True)
                    except Exception:
                        images[key + '_url'] = f"/uploads/{result.get(key)}"
            
            response = {'filename': filename, 'file_url': file_url, 'result': result}
            if images:
                response['images'] = images
            
            return jsonify(response)
        except Exception as e:
            return jsonify({'error': 'test generation error', 'details': str(e), 'file_url': file_url}), 500
    else:
        return jsonify({'error': 'file type not allowed'}), 400


@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """静态暴露上传目录下的文件，开发时方便前端直接访问上传后的图片。"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/model/status')
def model_status_route():
    """返回模型加载状态，便于前端或运维查看。"""
    status = load_model()
    return jsonify(status)


if __name__ == '__main__':
    # 使用环境变量 PORT 可覆盖默认端口（避免与系统服务冲突）。
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
