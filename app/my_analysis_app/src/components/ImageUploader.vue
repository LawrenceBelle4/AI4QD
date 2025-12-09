<template>
  <div class="image-uploader">
    <h2>文件操作</h2>

    <button @click="triggerUpload" class="upload-btn">
      上传图片
    </button>
    <input 
      type="file" 
      ref="fileInput" 
      @change="onFileChange" 
      style="display: none;" 
      accept="image/*"
    >

    <button @click="triggerBatchImport" class="batch-btn">
      批量导入
    </button>
    <p v-if="fileName">已选择文件：**{{ fileName }}**</p>

    <div v-if="originalImage" class="preview-wrapper">
      <h3>原始预览</h3>
      <img :src="originalImage" alt="原始图片预览" class="preview-image">
    </div>

    <div class="note">
        <p>支持拖拽上传或点击按钮选择文件。</p>
        <p>上传图片后，系统将自动进行 <strong>AI</strong> 智能识别和特性分析。</p>
    </div>
  </div>
</template>

<script setup>
import { ref, defineEmits, defineProps } from 'vue';

const props = defineProps({
  originalImage: String,
});

const emits = defineEmits(['file-uploaded']);
const fileInput = ref(null);
const fileName = ref('');

const triggerUpload = () => {
  fileInput.value.click();
};

const onFileChange = (event) => {
  const file = event.target.files[0];
  if (file) {
    fileName.value = file.name;
    emits('file-uploaded', file);
    event.target.value = ''; 
  }
};

const triggerBatchImport = () => {
  alert('批量导入功能待实现...'); 
};
</script>

<style scoped>
.image-uploader {
  display: flex;
  flex-direction: column;
  gap: 15px;
}
h2 {
  color: #409eff; 
  margin-bottom: 10px;
}
.upload-btn, .batch-btn {
  padding: 10px 15px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1em;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: background-color 0.3s;
}
.upload-btn {
  background-color: #409eff; 
  color: white;
}
.upload-btn:hover {
  background-color: #66b1ff;
}
.batch-btn {
  background-color: #f0f0f0; 
  color: #606266;
  border: 1px solid #dcdfe6;
}
.batch-btn:hover {
  background-color: #e4e7ed;
}
.note {
    margin-top: 20px;
    padding: 10px;
    border-left: 4px solid #409eff;
    background-color: #ecf5ff;
    font-size: 0.9em;
    color: #606266;
}
.note p {
    margin: 5px 0;
}

.preview-wrapper {
  margin-top: 12px;
}
.preview-image {
  width: 100%;
  max-height: 300px;
  object-fit: contain;
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.preview-wrapper h3 {
  color: #409eff;
  margin-bottom: 8px;
}
</style>