<template>
  <AppBreadcrumb :items="[{ label: '首页' }]" />
  <el-card>
    <div class="page-title" style="font-size: 16px; margin-bottom: 8px">欢迎</div>
    <div>从左侧进入报表模块或数据填报模块。</div>
  </el-card>
</template>

<script setup lang="ts">
import AppBreadcrumb from "../components/AppBreadcrumb.vue";
</script>
