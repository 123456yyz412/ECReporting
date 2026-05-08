<template>
  <div class="login-shell" :style="loginStyle">
    <el-card class="login-card">
      <div style="font-size: 18px; font-weight: 600; margin-bottom: 12px">登录</div>
      <el-form label-position="top">
        <el-form-item label="用户名">
          <el-input v-model="username" autocomplete="username" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="password" type="password" autocomplete="current-password" show-password />
        </el-form-item>
        <el-button type="primary" :loading="loading" style="width: 100%" @click="onLogin">登录</el-button>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { useAuthStore } from "../stores/auth";
import { http } from "../api/http";

const auth = useAuthStore();
const router = useRouter();

const username = ref("");
const password = ref("");
const loading = ref(false);
const pageBackground = ref<any | null>(null);

const loginStyle = computed(() => {
  const bg = pageBackground.value;
  const palette = bg?.palette || {};
  const style: Record<string, string> = {
    "--login-overlay": palette.page_overlay || "rgba(255,255,255,0.22)",
    "--login-card-bg": palette.panel_bg_strong || "rgba(255,255,255,0.88)",
    "--login-card-border": palette.panel_border || "rgba(148,163,184,0.22)",
    "--login-card-shadow": palette.panel_shadow || "0 18px 40px rgba(15,23,42,0.12)",
    "--login-text": palette.text_primary || "#0f172a"
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


async function onLogin() {
  loading.value = true;
  try {
    await auth.login(username.value, password.value);
    router.push("/");
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || "登录失败");
  } finally {
    loading.value = false;
  }
}

async function loadBranding() {
  const { data } = await http.get("/api/settings/branding/");
  pageBackground.value = data.page_background;
}

onMounted(() => {
  loadBranding().catch(() => undefined);
});
</script>

<style scoped>
.login-shell {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-position: center;
  background-size: cover;
  position: relative;
}

.login-shell::before {
  content: "";
  position: absolute;
  inset: 0;
  background: var(--login-overlay);
}

.login-card {
  width: 360px;
  position: relative;
  z-index: 1;
  background: var(--login-card-bg);
  border: 1px solid var(--login-card-border);
  box-shadow: var(--login-card-shadow);
  backdrop-filter: blur(20px) saturate(135%);
  color: var(--login-text);
}

.login-card :deep(.el-input__wrapper) {
  background: rgba(255, 255, 255, 0.45);
  box-shadow: 0 0 0 1px var(--login-card-border) inset;
}
</style>
