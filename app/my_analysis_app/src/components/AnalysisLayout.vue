<template>
  <div class="analysis-container">
    <header>
      <h1 class="app-title">
        <span class="title-icon">🤖</span>
        <span class="title-text">QD-SAM量子点智能识别与特性分析系统</span>
      </h1>
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
  justify-content: center;
  margin-bottom: 20px;
}

.app-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 26px;
  font-weight: 700;
  color: #0084ff;
  margin: 0;
  text-align: center;
}

.title-icon {
  font-size: 32px;
  display: inline-block;
  line-height: 1;
}

.title-text {
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