<template>
  <AppBreadcrumb :items="[{ label: '管理员' }]" />
  <el-card>
    <div class="page-title" style="font-size: 18px; margin-bottom: 8px">管理员</div>
    <div class="page-subtitle" style="margin-bottom: 16px">进入具体管理模块后，左上角路径支持点击返回父级页面。</div>
    <div style="display: flex; flex-wrap: wrap; gap: 12px">
      <el-button @click="router.push('/admin/datasources')">数据源实例</el-button>
      <el-button @click="router.push('/admin/users')">用户管理</el-button>
      <el-button @click="router.push('/admin/groups')">用户组管理</el-button>
      <el-button @click="router.push('/admin/branding')">站点设置</el-button>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { useRouter } from "vue-router";
import AppBreadcrumb from "../../components/AppBreadcrumb.vue";

const router = useRouter();
</script>
