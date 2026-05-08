<template>
  <el-container class="app-shell" :style="appStyle">
    <el-header class="app-header">
      <div style="display: flex; align-items: center; gap: 12px">
        <img v-if="branding.logo_url" :src="branding.logo_url" style="height: 28px" />
        <div style="font-size: 18px; font-weight: 600">{{ branding.company_name }}</div>
      </div>
      <div style="display: flex; align-items: center; gap: 12px">
        <div>{{ auth.me?.username }}</div>
        <el-button size="small" @click="onLogout">退出</el-button>
      </div>
    </el-header>
    <el-container class="app-body">
      <el-aside width="220px" class="app-aside">
        <el-menu :default-active="active" router class="app-menu">
          <el-menu-item index="/">首页</el-menu-item>
          <el-menu-item index="/reports">报表模块</el-menu-item>
          <el-menu-item index="/datafill">数据填报</el-menu-item>
          <el-sub-menu v-if="auth.me?.is_admin" index="/admin">
            <template #title>管理员</template>
            <el-menu-item index="/admin/datasources">数据源实例</el-menu-item>
            <el-menu-item index="/admin/users">用户</el-menu-item>
            <el-menu-item index="/admin/groups">用户组</el-menu-item>
            <el-menu-item index="/admin/branding">站点设置</el-menu-item>
          </el-sub-menu>
        </el-menu>
      </el-aside>
      <el-main class="app-main">
        <div class="page-content">
          <router-view />
        </div>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";
import { http } from "../api/http";

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();

const active = computed(() => route.path);

const branding = reactive<{ company_name: string; logo_url: string | null; page_background: any | null }>({
  company_name: "ECReporting",
  logo_url: null,
  page_background: null
});

const appStyle = computed(() => {
  const bg = branding.page_background;
  const palette = bg?.palette || {};
  const style: Record<string, string> = {
    "--page-overlay": palette.page_overlay || "rgba(255,255,255,0.22)",
    "--header-bg": palette.header_bg || "rgba(255,255,255,0.88)",
    "--sidebar-bg": palette.sidebar_bg || "rgba(255,255,255,0.84)",
    "--content-bg": palette.content_bg || "rgba(255,255,255,0.22)",
    "--panel-bg": palette.panel_bg || "rgba(255,255,255,0.74)",
    "--panel-bg-strong": palette.panel_bg_strong || "rgba(255,255,255,0.9)",
    "--panel-border": palette.panel_border || "rgba(148,163,184,0.22)",
    "--panel-shadow": palette.panel_shadow || "0 18px 40px rgba(15,23,42,0.12)",
    "--text-primary": palette.text_primary || "#0f172a",
    "--text-secondary": palette.text_secondary || "#475569",
    "--table-header-bg": "rgba(255,255,255,0.78)",
    "--table-row-bg": "rgba(255,255,255,0.34)",
    "--table-row-hover": "rgba(255,255,255,0.56)",
    "--field-bg": "rgba(255,255,255,0.72)"
  };
  if (!bg) return style;
  if (bg.kind === "custom" && bg.image_url) {
    style.backgroundImage = `url(${bg.image_url})`;
    return style;
  }
  if (bg.css) {
    style.backgroundImage = bg.css;
    return style;
  }
  return style;
});

async function loadBranding() {
  const { data } = await http.get("/api/settings/branding/");
  branding.company_name = data.company_name;
  branding.logo_url = data.logo_url;
  branding.page_background = data.page_background;
}

function onLogout() {
  auth.logout();
  router.push("/login");
}

onMounted(() => {
  loadBranding().catch(() => undefined);
});
</script>

<style scoped>
.app-shell {
  height: 100vh;
  position: relative;
  background-position: center;
  background-size: cover;
  color: var(--text-primary);
  overflow: hidden;
}

.app-shell::before {
  content: "";
  position: absolute;
  inset: 0;
  background: var(--page-overlay);
  pointer-events: none;
}

.app-header,
.app-aside,
.app-main {
  position: relative;
  z-index: 1;
}

.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--header-bg);
  border-bottom: 1px solid var(--panel-border);
  backdrop-filter: blur(18px) saturate(130%);
  box-shadow: var(--panel-shadow);
}

.app-body {
  flex: 1;
  min-height: 0;
  overflow: hidden;
}

.app-aside {
  border-right: 1px solid var(--panel-border);
  background: var(--sidebar-bg);
  backdrop-filter: blur(18px) saturate(130%);
  overflow: auto;
}

.app-main {
  min-height: 0;
  overflow: auto;
  background: var(--content-bg);
  scrollbar-width: thin;
  scrollbar-color: rgba(100, 116, 139, 0.45) transparent;
}

.page-content {
  min-height: 100%;
  padding: 12px;
  color: var(--text-primary);
}

.app-main::-webkit-scrollbar,
.app-aside::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.app-main::-webkit-scrollbar-track,
.app-aside::-webkit-scrollbar-track {
  background: transparent;
}

.app-main::-webkit-scrollbar-thumb,
.app-aside::-webkit-scrollbar-thumb {
  background: rgba(100, 116, 139, 0.35);
  border-radius: 999px;
}

.app-main:hover::-webkit-scrollbar-thumb,
.app-aside:hover::-webkit-scrollbar-thumb {
  background: rgba(100, 116, 139, 0.55);
}

.page-content :deep(.page-title) {
  color: var(--text-primary);
  font-weight: 700;
  letter-spacing: 0.01em;
}

.page-content :deep(.page-subtitle) {
  color: var(--text-secondary);
}

.app-menu {
  background: transparent;
  border-right: 0;
}

.app-aside :deep(.el-menu),
.app-aside :deep(.el-sub-menu__title),
.app-aside :deep(.el-menu-item) {
  background: transparent;
  color: var(--text-primary);
}

.app-aside :deep(.el-menu-item:hover),
.app-aside :deep(.el-sub-menu__title:hover) {
  background: rgba(255, 255, 255, 0.18);
}

.app-aside :deep(.el-menu-item.is-active) {
  background: var(--panel-bg);
  color: var(--text-primary);
}

.page-content :deep(.el-card),
.page-content :deep(.el-table),
.page-content :deep(.el-pagination),
.page-content :deep(.el-tabs__nav-wrap),
.page-content :deep(.el-input__wrapper),
.page-content :deep(.el-textarea__inner),
.page-content :deep(.el-select__wrapper),
.page-content :deep(.el-statistic),
.page-content :deep(.el-descriptions),
.page-content :deep(.el-empty),
.page-content :deep(.el-upload-dragger) {
  background: var(--panel-bg);
  border-color: var(--panel-border);
  box-shadow: var(--panel-shadow);
  backdrop-filter: blur(18px) saturate(130%);
}

.page-content :deep(.el-card) {
  border: 1px solid var(--panel-border);
}

.page-content :deep(.el-card__body),
.page-content :deep(.el-dialog__body),
.page-content :deep(.el-dialog__header),
.page-content :deep(.el-form-item__label),
.page-content :deep(.el-descriptions__label),
.page-content :deep(.el-descriptions__content),
.page-content :deep(.el-statistic__head),
.page-content :deep(.el-statistic__content),
.page-content :deep(.el-empty__description),
.page-content :deep(.el-table .cell) {
  color: var(--text-primary);
}

.page-content :deep(.el-table),
.page-content :deep(.el-table__inner-wrapper),
.page-content :deep(.el-table tr),
.page-content :deep(.el-table th.el-table__cell),
.page-content :deep(.el-table td.el-table__cell) {
  background: transparent;
}

.page-content :deep(.el-table th.el-table__cell) {
  background: var(--table-header-bg);
  color: var(--text-primary);
  font-weight: 700;
  border-bottom-color: var(--panel-border);
}

.page-content :deep(.el-table td.el-table__cell) {
  background: var(--table-row-bg);
  color: var(--text-primary);
  border-bottom-color: rgba(148, 163, 184, 0.18);
}

.page-content :deep(.el-table__body tr:hover > td.el-table__cell) {
  background: var(--table-row-hover);
}

.page-content :deep(.el-table__empty-block),
.page-content :deep(.el-table__body-wrapper),
.page-content :deep(.el-table__header-wrapper) {
  background: transparent;
}

.page-content :deep(.el-input__wrapper),
.page-content :deep(.el-select__wrapper),
.page-content :deep(.el-textarea__inner) {
  background: var(--field-bg);
  color: var(--text-primary);
}

.page-content :deep(.el-input__inner),
.page-content :deep(.el-textarea__inner),
.page-content :deep(.el-select__placeholder),
.page-content :deep(.el-select__selected-item),
.page-content :deep(input[type="file"]) {
  color: var(--text-primary);
}

.page-content :deep(.el-overlay-dialog) {
  backdrop-filter: blur(6px);
}

.page-content :deep(.el-dialog),
:deep(.el-dialog) {
  background: var(--panel-bg-strong);
  border: 1px solid var(--panel-border);
  box-shadow: var(--panel-shadow);
  backdrop-filter: blur(22px) saturate(135%);
}

.page-content :deep(.el-button:not(.el-button--primary):not(.el-button--success):not(.el-button--warning):not(.el-button--danger)),
.app-header :deep(.el-button:not(.el-button--primary):not(.el-button--success):not(.el-button--warning):not(.el-button--danger)) {
  background: rgba(255, 255, 255, 0.38);
  border-color: var(--panel-border);
  color: var(--text-primary);
}
</style>
