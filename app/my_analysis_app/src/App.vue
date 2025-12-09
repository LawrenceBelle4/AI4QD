<template>
  <AnalysisLayout />
</template>

<script setup>
// 导入主布局组件
// 注意路径：./components/ 意味着在当前目录下的 components 文件夹里找
import AnalysisLayout from './components/AnalysisLayout.vue';
</script>

<style>
/* 这里放置全局样式 */

/* 重置浏览器默认的 margin 和 padding，确保布局占满全屏 */
body, html {
  margin: 0;
  padding: 0;
  height: 100%;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  background-color: #f5f7fa; /* 设置一个柔和的背景色 */
}

#app {
  height: 100%;
}
</style>