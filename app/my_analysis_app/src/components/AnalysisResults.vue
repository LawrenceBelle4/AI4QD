<template>
  <div class="analysis-results">
    <h2>分析结果</h2>

    <div class="result-section">
      <h3>识别结果</h3>
      <div v-if="loading" class="loading-container">
        <div class="spinner"></div>
        <p class="loading-text">模型处理中，请稍候...</p>
      </div>
      <div v-else-if="recognitionImage || maskImage" class="image-grid">
        <div v-if="recognitionImage" class="image-cell">
          <img :src="recognitionImage" alt="覆盖结果" class="small-image">
          <label>覆盖图</label>
        </div>
        <div v-if="maskImage" class="image-cell">
          <img :src="maskImage" alt="掩码" class="small-image">
          <label>二值掩码</label>
        </div>
        </div>
      <p v-else class="placeholder">请在左侧上传图片以进行识别...</p>
    </div>

    <hr>

    <div class="result-section">
      <h3>统计分析结果</h3>
      
      <div v-if="loading" class="loading-container">
        <div class="skeleton-stat-item" v-for="i in 4" :key="i"></div>
      </div>
      <div v-else-if="statisticsData || histogramImage" class="stats-analysis-layout">
        
        <div class="chart-container">
            <div class="container-header">
                <label v-if="histogramImage" class="chart-label">直径分布直方图</label>
            </div>
            <div class="histogram-wrapper">
                <div v-if="histogramImage" class="histogram-display">
                    <img :src="histogramImage" alt="直方图" class="full-width-image">
                </div>
                <div v-else class="chart-placeholder">
                    <p>暂无直方图</p>
                </div>
            </div>
        </div>

        <div class="key-stats-container">
            <div class="container-header">
                <h4 style="margin: 0; color: #303133; font-size: 14px; font-weight: 600;">量子点统计数据</h4>
            </div>
            <div class="key-stats">
              <div class="stat-item">
                <span class="label">量子点数量：</span>
                <span class="value">{{ count}}个</span>
              </div>
              <div class="stat-item">
                <span class="label">量子点密度：</span>
                <span class="value">{{ scientificDensity}}个/c㎡</span>
              </div>
              <div class="stat-item">
                <span class="label">量子点平均直径：</span>
                <span class="value">{{ averageDiameter }}nm</span>
              </div>
              <div class="stat-item">
                <span class="label">量子点直径方差：</span> 
                <span class="value">{{ areaMean }}nm²</span>
              </div>
            </div>
        </div>
        
      </div>
      <p v-else class="placeholder">等待上传文件并进行分析...</p>
    </div>
  </div>
</template>

<script setup>
import { defineProps, computed } from 'vue';

const props = defineProps({
  recognitionImage: String,
  statisticsData: Object,
  statisticsRaw: Object,
  maskImage: String,
  histogramImage: String, // 仍然需要接收这个 prop
  loading: Boolean,
});


const scientificDensity = computed(() => {
  const rawDensity = density.value;

  // 1. 检查是否是有效数字
  if (typeof rawDensity === 'number' && rawDensity !== '—') {
    // 2. 计算最终的密度值： rawDensity * (10^14)
    const finalValue = rawDensity * (10 ** 14);

    // 3. 使用 toPrecision(2)
    // toPrecision(2) 表示保留 2 个有效数字，即：
    // 1.123 x 10^11 会变为 1.1 x 10^11
    // 9.876 x 10^11 会变为 9.9 x 10^11
    // 如果想要精确到 1 位小数，即 1.1...，需要保留 2 位有效数字 (如 1.1e+11)。
    // 如果只需要保留整数位，则使用 toPrecision(1) (如 1e+11)。
    
    // 如果您想要保留整数位 (1) 和小数点后一位 (0.1)，即总共两位有效数字，请使用 2：
    return finalValue.toPrecision(2).replace('e+', ' × 10^');
    
    // 如果您确定只需要保留一位有效数字 (1 x 10^11)，请使用 1：
    // return finalValue.toPrecision(1).replace('e+', ' × 10^');
  }
  return '—'; // 返回占位符
});


// 兼容后端不同字段名，提供友好展示
const stats = computed(() => props.statisticsData || {});

const count = computed(() => {
  return (
    stats.value.quantumDotCount ?? stats.value.quantum_dot_count ?? stats.value.count ?? '—'
  );
});

const density = computed(() => {
  // 注意：此处计算表达式 {{ density *(10**14)}} 已经放在模板中
  return (
    stats.value.density ?? stats.value.density_per_pixel ?? stats.value.density_per_px ?? '—'
  );
});

const averageDiameter = computed(() => {
  return (
    stats.value.averageDiameter ?? stats.value.average_diameter_px ?? stats.value.avg_diameter ?? '—'
  );
});

const areaMean = computed(() => {
  return (
    stats.value.diameter_variance ?? stats.value.diameterVariance ?? stats.value.area_mean_px2 ?? '—'
  );
});
</script>

<style scoped>
/* 保持原有样式，仅修改/添加与新布局相关的部分 */

.analysis-results {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
h2 {
  color: #409eff;
  margin-bottom: 15px;
}
h3 {
  color: #606266;
  border-bottom: 2px solid #ebeef5;
  padding-bottom: 5px;
  margin-bottom: 15px;
}
hr {
    border: 0;
    border-top: 1px solid #ebeef5;
    margin: 20px 0;
}

/* --- 统计分析结果的新布局样式 --- */
.stats-analysis-layout {
    display: flex;
    gap: 24px;
    align-items: stretch;
}

.chart-container {
    flex: 0 0 45%;
    padding: 0;
    display: flex;
    flex-direction: column;
}

.key-stats-container {
    flex: 0 0 55%;
    padding: 0;
    display: flex;
    flex-direction: column;
}

.container-header {
    height: 40px;
    display: flex;
    align-items: center;
    margin-bottom: 8px;
}

.chart-label {
    font-weight: 600;
    color: #303133;
    font-size: 14px;
    margin: 0;
}

.histogram-wrapper {
    flex: 1;
    display: flex;
}

.histogram-display {
    border: 1px solid #ebeef5;
    padding: 10px;
    border-radius: 4px;
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
}

.full-width-image {
    width: 100%;
    height: auto;
    border-radius: 4px;
}

.key-stats {
    display: grid;
    grid-template-columns: 1fr;
    gap: 15px;
    padding: 15px;
    background-color: #f9f9f9;
    border-radius: 4px;
    border: 1px solid #ebeef5;
    flex: 1;
}
/* -------------------------------- */

/* 识别结果的 image-grid 保持不变，但移除了 histogramImage 的逻辑 */
.image-grid {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  justify-content: flex-start;
  align-items: flex-start;
}
.image-cell {
  flex: 0 1 calc(50% - 8px);
  text-align: center;
  min-width: 200px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}
.image-cell label {
  font-weight: 600;
  color: #303133;
  font-size: 14px;
  margin: 0;
}
.small-image {
  width: 100%;
  height: 240px;
  object-fit: contain;
  border-radius: 4px;
  box-shadow: 0 0 8px rgba(0,0,0,0.12);
  background-color: #f5f5f5;
}
/* -------------------------------- */

.placeholder {
  color: #909399;
  text-align: center;
  padding: 50px 0;
  border: 1px dashed #dcdfe6;
  border-radius: 4px;
}

.stat-item {
    font-size: 1em;
    padding: 0;
    line-height: 1.5;
}
.label {
    font-weight: bold;
    color: #303133;
}
.value {
    color: #409eff;
    font-weight: 600;
}

.chart-placeholder {
    height: 300px;
    display: flex;
    justify-content: center;
    align-items: center;
    background-color: #fafafa;
    border: 1px dashed #dcdfe6;
    margin-top: 10px;
    border-radius: 4px;
}


.loading-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  min-height: 200px;
}

.spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #409eff;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  margin-top: 12px;
  color: #606266;
  font-size: 14px;
}

.skeleton-stat-item {
  height: 20px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
  margin-bottom: 10px;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
</style>