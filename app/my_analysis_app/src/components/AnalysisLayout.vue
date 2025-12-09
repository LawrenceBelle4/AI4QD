<template>
  <div class="analysis-container">
    <header>
      <div class="header-top">
        <div class="logo">
          <span class="logo-text">AI</span>
          <div class="quantum-sphere">
            <div class="quantum-dot" v-for="i in 12" :key="i"></div>
          </div>
        </div>
        <h1 class="app-title">QD-SAM量子点智能识别与特性分析系统</h1>
      </div>
    </header>
    <main class="content-wrapper">
      <section class="left-panel">
        <ImageUploader :original-image="originalImage" @file-uploaded="handleFileUpload" />
      </section>

      <section class="right-panel">
        <AnalysisResults 
          :recognition-image="recognitionImage"
          :mask-image="maskImage"
          :histogram-image="histogramImage"
          :statistics-data="statisticsData"
          :statistics-raw="statisticsDataRaw"
          :loading="loading"
        />
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import ImageUploader from './ImageUploader.vue';
import AnalysisResults from './AnalysisResults.vue';

const title = ref('QD-SAM量子点智能识别与特性分析系统'); // 系统标题
const originalImage = ref(null); // 本地上传的原图预览（左侧显示）
const recognitionImage = ref(null); // 后端/模型返回的识别结果（覆盖图）
const maskImage = ref(null); // 后端返回的二值掩码展示
const histogramImage = ref(null); // 后端返回的直方图
const statisticsData = ref(null);
const statisticsDataRaw = ref(null);
const loading = ref(false);

const handleFileUpload = async (file) => {
  if (!file) return;
  console.log('文件已上传:', file.name);

    // 先在前端显示本地预览（左侧）
    try {
      loading.value = true;
      const localUrl = URL.createObjectURL(file);
      originalImage.value = localUrl;

    const form = new FormData();
    form.append('file', file);

    const resp = await fetch('http://localhost:5001/upload', {
      method: 'POST',
      body: form,
    });
    const data = await resp.json();
    console.log('Upload response:', resp.status, data);
    if (!resp.ok) {
      throw new Error(data.error || 'upload failed');
    }

    // 保存原始返回供调试
    statisticsDataRaw.value = data;

    // 后端返回 { filename, file_url, result, images }
    statisticsData.value = data.result ? data.result : data;

    // images 字段里包含各处理图的 URL（如果后端生成）
    if (data.images) {
      recognitionImage.value = data.images.result_image_url || data.file_url || null;
      maskImage.value = data.images.mask_image_url || null;
      histogramImage.value = data.images.histogram_image_url || null;
    } else {
      // 兼容老版：直接使用 file_url 作为识别图
      recognitionImage.value = data.file_url || null;
      maskImage.value = null;
      histogramImage.value = null;
    }
  } catch (err) {
    console.error(err);
    alert('上传或分析时发生错误：' + (err.message || err));
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.analysis-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  padding: 20px;
}

header {
  display: flex;
  justify-content: flex-start;
  margin-bottom: 30px;
}

.header-top {
  display: flex;
  align-items: center;
  gap: 30px;
  width: 100%;
}

/* Logo 样式 */
.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

.logo-text {
  font-size: 32px;
  font-weight: 800;
  color: #0084ff;
  letter-spacing: 2px;
  font-family: 'Arial Black', Arial, sans-serif;
}

/* 动态量子点球状 */
.quantum-sphere {
  position: relative;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.quantum-dot {
  position: absolute;
  width: 8px;
  height: 8px;
  background: radial-gradient(circle at 30% 30%, #ffeb3b, #ff9800);
  border-radius: 50%;
  animation: float 3s ease-in-out infinite;
}

.quantum-dot:nth-child(1) { left: 50%; top: 0%; animation-delay: 0s; }
.quantum-dot:nth-child(2) { left: 85%; top: 15%; animation-delay: 0.15s; }
.quantum-dot:nth-child(3) { left: 100%; top: 50%; animation-delay: 0.3s; }
.quantum-dot:nth-child(4) { left: 85%; top: 85%; animation-delay: 0.45s; }
.quantum-dot:nth-child(5) { left: 50%; top: 100%; animation-delay: 0.6s; }
.quantum-dot:nth-child(6) { left: 15%; top: 85%; animation-delay: 0.75s; }
.quantum-dot:nth-child(7) { left: 0%; top: 50%; animation-delay: 0.9s; }
.quantum-dot:nth-child(8) { left: 15%; top: 15%; animation-delay: 1.05s; }
.quantum-dot:nth-child(9) { left: 65%; top: 35%; animation-delay: 1.2s; }
.quantum-dot:nth-child(10) { left: 35%; top: 65%; animation-delay: 1.35s; }
.quantum-dot:nth-child(11) { left: 65%; top: 65%; animation-delay: 1.5s; }
.quantum-dot:nth-child(12) { left: 35%; top: 35%; animation-delay: 1.65s; }

@keyframes float {
  0%, 100% { transform: translate(0, 0) scale(1); opacity: 0.8; }
  50% { transform: translate(0, -8px) scale(1.1); opacity: 1; }
}

.app-title {
  font-size: 26px;
  font-weight: 700;
  color: #0084ff;
  margin: 0;
  text-align: center;
  flex: 1;
  letter-spacing: 0.5px;
}

.content-wrapper {
  display: flex;
  flex: 1;
  gap: 20px;
  overflow: hidden; 
}
.left-panel, .right-panel {
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  background: #fff;
  overflow: auto; 
}

/* 页面比例调整：从固定宽度改为 1:3 比例 */
.left-panel {
  flex: 1; /* 左侧占据 1 份 */
  max-width: 350px; /* 设置最大宽度，防止在大屏幕上过大 */
}
.right-panel {
  flex: 3; /* 右侧占据 3 份 */
}
</style>