"""
集成仓库内 SAM2 推理的模型接口。

实现策略：
- 尝试加载仓库中 `演示` 下的 SAM2 配置与权重（如果存在），并初始化自动掩码生成器（`SAM2AutomaticMaskGenerator`）。
- 在 `predict(image_path)` 中，使用 mask generator 生成掩码，做简单后处理（面积过滤、去重），并返回可序列化的统计信息。
- 如果模型或依赖缺失，则降级回随机占位结果（保持兼容现有后端路由）。

注意：真实部署时请在服务器环境中通过 `pip install -r backend/requirements.txt` 安装依赖，并根据可用 GPU 修改 device 设置。
"""
import os
import sys
import math
import numpy as np
import cv2
from PIL import Image
import uuid
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

_MODEL_LOADED = False
_LOAD_ERROR = None
_MASK_GENERATOR = None
_SAM_MODEL = None
_PREDICTOR = None
_DEVICE = 'cpu'


def _try_load_model():
  global _MODEL_LOADED, _LOAD_ERROR, _MASK_GENERATOR, _SAM_MODEL, _DEVICE
  try:
    import torch
    import cv2

    # Ensure project root is on sys.path so local sam2 package can be imported
    ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if ROOT not in sys.path:
      sys.path.append(ROOT)

    # candidate paths inside repository
    sam_checkpoint = os.path.join(ROOT, '演示', 'checkpoint', 'sam2.1_hiera_large.pt')
    # config file in repo is at 演示/configs/sam2.1_hiera_l.yaml
    model_cfg = os.path.join(ROOT, '演示', 'configs', 'sam2.1_hiera_l.yaml')
    fine_tuned = os.path.join(ROOT, '演示', 'train_quantum', 'sam2_finetuned_final.torch')

    # import builder + automatic mask generator
    from sam2.build_sam import build_sam2
    from sam2.automatic_mask_generator import SAM2AutomaticMaskGenerator
    # predictor helper used in training scripts
    try:
      from sam2.sam2_image_predictor import SAM2ImagePredictor
    except Exception:
      SAM2ImagePredictor = None

    # pick device
    _DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'

    # build base sam2 model
    # Some sam2/build logic uses hydra and expects config paths relative to a project folder.
    old_cwd = os.getcwd()
    try:
      demo_dir = os.path.join(ROOT, '演示')
      if os.path.isdir(demo_dir):
        os.chdir(demo_dir)
        # use relative paths inside 演示 so hydra's search can find 'configs/...'
        model_cfg_rel = os.path.join('configs', 'sam2.1', os.path.basename(model_cfg))
        sam_checkpoint_rel = os.path.join('checkpoint', os.path.basename(sam_checkpoint))
        _SAM_MODEL = build_sam2(model_cfg_rel, sam_checkpoint_rel, device=_DEVICE, apply_postprocessing=False)
      else:
        # fallback to absolute paths
        _SAM_MODEL = build_sam2(model_cfg, sam_checkpoint, device=_DEVICE, apply_postprocessing=False)
    finally:
      os.chdir(old_cwd)

    # load fine-tuned weights if available
    if os.path.exists(fine_tuned):
      weights = torch.load(fine_tuned, map_location=_DEVICE)
      _SAM_MODEL.load_state_dict(weights)

    _SAM_MODEL.eval()

    # create automatic mask generator tuned for small object detection (similar to repo code)
    _MASK_GENERATOR = SAM2AutomaticMaskGenerator(
      _SAM_MODEL,
      points_per_side=64,
      pred_iou_thresh=0.6,
      stability_score_thresh=0.5,
      crop_n_layers=1,
      crop_n_points_downscale_factor=1,
    )

    # create a SAM2ImagePredictor if available; this provides set_image(...) used by some APIs
    if SAM2ImagePredictor is not None:
      try:
        _PREDICTOR = SAM2ImagePredictor(_SAM_MODEL)
      except Exception:
        _PREDICTOR = None

    _MODEL_LOADED = True
    _LOAD_ERROR = None
  except Exception as e:
    _MODEL_LOADED = False
    _LOAD_ERROR = str(e)


# 尝试加载模型（导入时进行一次尝试）
def load_model():
  """显式触发模型加载。返回 dict 状态，方便上层服务调用并上报状态。"""
  global _MODEL_LOADED, _LOAD_ERROR
  if _MODEL_LOADED:
    return {'loaded': True, 'device': _DEVICE, 'error': None}
  _try_load_model()
  return {'loaded': _MODEL_LOADED, 'device': _DEVICE, 'error': _LOAD_ERROR}


# 默认导入时尝试加载一次，但推荐服务在启动时显式调用 `load_model()` 来确认状态
_try_load_model()


def _simple_dedupe(masks, overlap_thresh=0.5):
  """简单的基于稳定性分数的去重实现，保留高置信度的掩码并移除高度重叠的。"""
  if not masks:
    return masks
  sorted_masks = sorted(masks, key=lambda x: x.get('stability_score', 0), reverse=True)
  keep = [True] * len(sorted_masks)

  def overlap(m1, m2):
    a = m1.astype(bool)
    b = m2.astype(bool)
    return np.logical_and(a, b).sum()

  for i in range(len(sorted_masks)):
    if not keep[i]:
      continue
    mi = sorted_masks[i]['segmentation']
    ai = sorted_masks[i].get('area', mi.astype(bool).sum())
    for j in range(i + 1, len(sorted_masks)):
      if not keep[j]:
        continue
      mj = sorted_masks[j]['segmentation']
      aj = sorted_masks[j].get('area', mj.astype(bool).sum())
      ov = overlap(mi, mj)
      if ov > 0:
        smaller = min(ai, aj)
        if smaller > 0 and (ov / smaller) > overlap_thresh:
          keep[j] = False

  return [m for k, m in zip(keep, sorted_masks) if k]


def predict(image_path: str):
  """对单张图片进行推理并返回统计结果。

  返回结构（示例）:
    {
    'quantumDotCount': int,
    'density_per_pixel': float,
    'average_diameter_px': float,
    'area_mean_px2': float,
    'note': optional string when falling back or error
    }
  """
  # If model not loaded, fall back to previous random stub
  if not _MODEL_LOADED:
    import random
    return {
      'quantumDotCount': random.randint(100, 1000),
      'density_per_pixel': None,
      'average_diameter_px': None,
      'area_mean_px2': None,
      'note': f'model not loaded: {_LOAD_ERROR}'
    }

  try:
    # read image as RGB numpy
    img = Image.open(image_path).convert('RGB')
    img = np.array(img)

    # keep original size for density calculation
    H, W = img.shape[:2]

    # resize to 512x512 as repo does
    img_resized = cv2.resize(img, (512, 512))

    # ensure predictor has image set (some mask code expects this)
    try:
      if _PREDICTOR is not None:
        _PREDICTOR.set_image(img_resized)
    except Exception:
      # ignore but allow mask generator to run
      pass

    # generate masks using automatic generator
    masks = _MASK_GENERATOR.generate(img_resized)

    # area filtering (same threshold as repo)
    filtered = [m for m in masks if m.get('area', 0) <= 10000]

    # deduplicate
    try:
      # try to use repo's more advanced function if available
      # otherwise use internal simple dedupe
      from importlib import util
      ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
      dist_path = os.path.join(ROOT, '演示', 'train_quantum', 'distributions.py')
      if os.path.exists(dist_path):
        spec = util.spec_from_file_location('distmod', dist_path)
        distmod = util.module_from_spec(spec)
        spec.loader.exec_module(distmod)
        if hasattr(distmod, 'remove_overlapping_masks_nms'):
          dedup = distmod.remove_overlapping_masks_nms(filtered, overlap_threshold=0.5)
        else:
          dedup = _simple_dedupe(filtered)
      else:
        dedup = _simple_dedupe(filtered)
    except Exception:
      dedup = _simple_dedupe(filtered)

    count = len(dedup)

    # compute areas and equivalent diameters (in pixels)
    areas = [m.get('area', int(np.sum(m['segmentation'].astype(bool)))) for m in dedup]
    if areas:
      area_mean = float(np.mean(areas))
      # equivalent diameter: sqrt(4*area/pi)
      diameters = [math.sqrt(4.0 * a / math.pi) for a in areas]
      avg_diam = float(np.mean(diameters))
      diameter_variance = float(np.var(diameters))  # 直径方差
    else:
      area_mean = 0.0
      avg_diam = 0.0
      diameter_variance = 0.0

    density_per_pixel = float(count) / float(H * W) if (H * W) > 0 else 0.0

    print(f'[DEBUG] Starting visualization: count={count}, diameters={len(diameters) if "diameters" in locals() else 0}')

    # --- 生成并保存可视化结果：掩码、覆盖图、以及直方图 ---
    try:
      uploads_dir = os.path.join(os.path.dirname(__file__), 'uploads')
      os.makedirs(uploads_dir, exist_ok=True)

      base = os.path.splitext(os.path.basename(image_path))[0]
      suffix = uuid.uuid4().hex[:8]
      result_fname = f"{base}_result_{suffix}.png"
      mask_fname = f"{base}_mask_{suffix}.png"
      hist_fname = f"{base}_hist_{suffix}.png"

      print(f'[DEBUG] Files to save: result={result_fname}, mask={mask_fname}, hist={hist_fname}')

      # 合并掩码（512x512）
      mask_combined = np.zeros((img_resized.shape[0], img_resized.shape[1]), dtype=np.uint8)
      for m in dedup:
        seg = m.get('segmentation')
        if seg is None:
          continue
        seg_arr = seg.astype(np.uint8)
        mask_combined[seg_arr > 0] = 255

      # 保存二值掩码（保存为 PNG）
      mask_out_path = os.path.join(uploads_dir, mask_fname)
      cv2.imwrite(mask_out_path, mask_combined)
      print(f'[DEBUG] Mask saved to {mask_out_path}')

      # 将掩码缩放回原始尺寸并 overlay 到原始图像上
      mask_large = cv2.resize(mask_combined, (W, H), interpolation=cv2.INTER_NEAREST)
      # 原始图像为 RGB，转换为 BGR 保存/显示
      orig_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
      overlay = orig_bgr.copy()
      # 简单半透明红色覆盖
      red = np.array([0, 0, 255], dtype=np.uint8)
      overlay[mask_large > 0] = (overlay[mask_large > 0] * 0.5 + red * 0.5).astype(np.uint8)
      result_out_path = os.path.join(uploads_dir, result_fname)
      cv2.imwrite(result_out_path, overlay)

      print(f'[DEBUG] Result overlay saved to {result_out_path}')

      # 计算形状因子（基于周长和面积）
      shapes = []
      for m in dedup:
        seg = m.get('segmentation')
        if seg is None:
          continue
        seg_u8 = (seg.astype(np.uint8) * 255)
        # 将单个掩码放大到原始尺寸以计算周长更稳定
        seg_large = cv2.resize(seg_u8, (W, H), interpolation=cv2.INTER_NEAREST)
        contours, _ = cv2.findContours(seg_large, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        perim = 0.0
        if contours:
          perim = sum([cv2.arcLength(c, True) for c in contours])
        area_px = m.get('area', int(np.sum(seg.astype(bool))))
        if perim > 0:
          shape_factor = (4.0 * math.pi * float(area_px)) / (perim * perim)
        else:
          shape_factor = 0.0
        shapes.append(float(shape_factor))

      # 画直方图（直径 & 形状因子）并保存
      try:
        plt.figure(figsize=(8, 4))
        plt.subplot(1, 2, 1)
        if len(diameters) > 0:
          plt.hist(diameters, bins=30, color='C0', edgecolor='black')
        plt.xlabel('Equivalent diameter (pixel)')
        plt.title('D')

        plt.subplot(1, 2, 2)
        if len(shapes) > 0:
          plt.hist(shapes, bins=30, color='C1', edgecolor='black')
        plt.xlabel('Blaschke shape factor')
        plt.title('I')

        hist_out_path = os.path.join(uploads_dir, hist_fname)
        plt.tight_layout()
        plt.savefig(hist_out_path, dpi=150)
        plt.close()
        print(f'[DEBUG] Histogram saved to {hist_out_path}')
      except Exception as hist_e:
        print(f'[DEBUG] Histogram save failed: {str(hist_e)}')
        hist_out_path = None

      print(f'[DEBUG] Returning result with images: result={result_fname}, mask={mask_fname}, hist={hist_fname}')
      return {
        'quantumDotCount': int(count),
        'density_per_pixel': density_per_pixel,
        'average_diameter_px': avg_diam,
        'diameter_variance': diameter_variance,
        # 文件名（相对 uploads/），上层路由会构建完整 URL
        'result_image': result_fname,
        'mask_image': mask_fname,
        'histogram_image': os.path.basename(hist_out_path) if hist_out_path else None,
      }
    except Exception as e:
      # 如果可视化过程失败，仍返回数值结果并在 note 中说明
      print(f'[DEBUG] Visualization block failed: {str(e)}')
      import traceback
      traceback.print_exc()
      return {
        'quantumDotCount': int(count),
        'density_per_pixel': density_per_pixel,
        'average_diameter_px': avg_diam,
        'diameter_variance': diameter_variance,
        'note': f'visualization error: {str(e)}'
      }

  except Exception as e:
    return {'error': 'inference error', 'details': str(e)}

