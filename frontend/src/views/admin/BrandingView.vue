<template>
  <AppBreadcrumb :items="breadcrumbItems" />
  <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px">
    <div class="page-title" style="font-size: 18px">站点设置</div>
    <div style="display: flex; gap: 8px">
      <el-button @click="restoreWhiteSkin">恢复全白原皮</el-button>
      <el-button @click="load">刷新</el-button>
      <el-button type="primary" :loading="saving" @click="save">保存</el-button>
    </div>
  </div>

  <el-card>
    <el-form label-position="top">
      <el-form-item label="公司名称">
        <el-input v-model="companyName" />
      </el-form-item>
      <el-form-item label="公司标识">
        <div style="display: flex; align-items: center; gap: 12px">
          <img v-if="logoUrl" :src="logoUrl" style="height: 40px" />
          <input type="file" accept="image/*" @change="onFile" />
        </div>
      </el-form-item>
      <el-form-item label="页面背景">
        <div style="width: 100%">
          <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px">
            <div style="font-weight: 600">内置背景</div>
            <div style="color: #64748b">适合跨境、电商、数据、科技主题</div>
          </div>
          <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 12px; margin-bottom: 20px">
            <div
              v-for="bg in builtins"
              :key="`builtin-${bg.key}`"
              @click="selectBuiltin(bg)"
              :style="cardStyle(isSelected('builtin', bg.key))"
            >
              <div :style="previewShellStyle(bg)">
                <div :style="previewHeaderStyle(bg)"></div>
                <div style="display: flex; gap: 8px; padding: 10px; height: 84px">
                  <div :style="previewSidebarStyle(bg)"></div>
                  <div style="flex: 1; display: grid; grid-template-columns: 1fr 1fr; gap: 8px">
                    <div :style="previewPanelStyle(bg)"></div>
                    <div :style="previewPanelStyle(bg)"></div>
                    <div :style="previewWidePanelStyle(bg)"></div>
                  </div>
                </div>
              </div>
              <div style="margin-top: 8px; font-weight: 600">{{ bg.name }}</div>
              <div style="font-size: 12px; color: #64748b">{{ bg.theme }}</div>
            </div>
          </div>

          <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px">
            <div style="font-weight: 600">自定义背景</div>
            <div style="display: flex; align-items: center; gap: 12px">
              <el-input v-model="customName" placeholder="背景名称" style="width: 180px" />
              <input type="file" accept="image/*" @change="onBackgroundFile" />
              <el-button type="primary" :loading="uploadingBg" @click="uploadBackground">上传背景</el-button>
            </div>
          </div>
          <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 12px">
            <div
              v-for="bg in customs"
              :key="`custom-${bg.key}`"
              @click="selectCustom(bg)"
              :style="cardStyle(isSelected('custom', bg.key))"
            >
              <div :style="previewShellStyle(bg)">
                <div :style="previewHeaderStyle(bg)"></div>
                <div style="display: flex; gap: 8px; padding: 10px; height: 84px">
                  <div :style="previewSidebarStyle(bg)"></div>
                  <div style="flex: 1; display: grid; grid-template-columns: 1fr 1fr; gap: 8px">
                    <div :style="previewPanelStyle(bg)"></div>
                    <div :style="previewPanelStyle(bg)"></div>
                    <div :style="previewWidePanelStyle(bg)"></div>
                  </div>
                </div>
              </div>
              <div style="display: flex; align-items: center; justify-content: space-between; margin-top: 8px; gap: 8px">
                <div style="font-weight: 600; overflow: hidden; text-overflow: ellipsis; white-space: nowrap">{{ bg.name }}</div>
                <el-button size="small" type="danger" @click.stop="removeCustom(bg)">删除</el-button>
              </div>
            </div>
          </div>
        </div>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { http } from "../../api/http";
import AppBreadcrumb from "../../components/AppBreadcrumb.vue";

const companyName = ref("");
const logoUrl = ref<string | null>(null);
const file = ref<File | null>(null);
const saving = ref(false);
const builtins = ref<any[]>([]);
const customs = ref<any[]>([]);
const selectedKind = ref<"builtin" | "custom">("builtin");
const selectedValue = ref("");
const customName = ref("");
const customFile = ref<File | null>(null);
const uploadingBg = ref(false);
const breadcrumbItems = [
  { label: "管理员", to: "/admin" },
  { label: "站点设置" }
];

async function load() {
  const [brandingResp, backgroundsResp] = await Promise.all([
    http.get("/api/settings/branding/"),
    http.get("/api/settings/backgrounds/")
  ]);
  const data = brandingResp.data;
  companyName.value = data.company_name;
  logoUrl.value = data.logo_url;
  selectedKind.value = data.page_background?.kind || "builtin";
  selectedValue.value = data.page_background?.key || "";
  builtins.value = backgroundsResp.data.builtins || [];
  customs.value = backgroundsResp.data.customs || [];
  file.value = null;
}

function onFile(e: Event) {
  const input = e.target as HTMLInputElement;
  file.value = input.files?.[0] || null;
}

function onBackgroundFile(e: Event) {
  const input = e.target as HTMLInputElement;
  customFile.value = input.files?.[0] || null;
}

function isSelected(kind: "builtin" | "custom", key: string) {
  return selectedKind.value === kind && selectedValue.value === key;
}

function selectBuiltin(bg: any) {
  selectedKind.value = "builtin";
  selectedValue.value = bg.key;
}

function selectCustom(bg: any) {
  selectedKind.value = "custom";
  selectedValue.value = bg.key;
}

function restoreWhiteSkin() {
  selectedKind.value = "builtin";
  selectedValue.value = "plain-white";
  ElMessage.success("已切换为全白原皮，保存后生效");
}

function cardStyle(selected: boolean) {
  return {
    padding: "10px",
    borderRadius: "10px",
    cursor: "pointer",
    border: selected ? "2px solid #2563eb" : "1px solid #dbeafe",
    background: selected ? "rgba(219,234,254,0.55)" : "#fff"
  };
}

function previewShellStyle(bg: any) {
  return {
    height: "110px",
    borderRadius: "10px",
    overflow: "hidden",
    backgroundImage: bg.kind === "custom" ? `url(${bg.image_url})` : bg.css,
    backgroundSize: "cover",
    backgroundPosition: "center",
    boxShadow: bg?.palette?.panel_shadow || "0 8px 24px rgba(15,23,42,0.12)"
  };
}

function previewHeaderStyle(bg: any) {
  return {
    height: "16px",
    background: bg?.palette?.header_bg || "rgba(255,255,255,0.85)",
    borderBottom: `1px solid ${bg?.palette?.panel_border || "rgba(148,163,184,0.22)"}`,
    backdropFilter: "blur(12px)"
  };
}

function previewSidebarStyle(bg: any) {
  return {
    width: "42px",
    height: "100%",
    borderRadius: "8px",
    background: bg?.palette?.sidebar_bg || "rgba(255,255,255,0.78)",
    border: `1px solid ${bg?.palette?.panel_border || "rgba(148,163,184,0.22)"}`,
    backdropFilter: "blur(12px)"
  };
}

function previewPanelStyle(bg: any) {
  return {
    height: "28px",
    borderRadius: "8px",
    background: bg?.palette?.panel_bg || "rgba(255,255,255,0.7)",
    border: `1px solid ${bg?.palette?.panel_border || "rgba(148,163,184,0.22)"}`,
    backdropFilter: "blur(12px)"
  };
}

function previewWidePanelStyle(bg: any) {
  return {
    gridColumn: "1 / span 2",
    height: "40px",
    borderRadius: "8px",
    background: bg?.palette?.panel_bg_strong || bg?.palette?.panel_bg || "rgba(255,255,255,0.8)",
    border: `1px solid ${bg?.palette?.panel_border || "rgba(148,163,184,0.22)"}`,
    backdropFilter: "blur(12px)"
  };
}

async function uploadBackground() {
  if (!customFile.value) {
    ElMessage.warning("请先选择图片");
    return;
  }
  uploadingBg.value = true;
  try {
    const fd = new FormData();
    fd.append("name", customName.value || customFile.value.name);
    fd.append("image", customFile.value);
    const { data } = await http.post("/api/admin/settings/backgrounds/", fd, {
      headers: { "Content-Type": "multipart/form-data" }
    });
    customs.value = [data, ...customs.value];
    selectedKind.value = "custom";
    selectedValue.value = data.key;
    customName.value = "";
    customFile.value = null;
    ElMessage.success("背景已上传");
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || e?.response?.data?.name?.[0] || "上传失败");
  } finally {
    uploadingBg.value = false;
  }
}

async function removeCustom(bg: any) {
  try {
    await ElMessageBox.confirm(`确认删除自定义背景“${bg.name}”吗？`, "删除背景", { type: "warning" });
    await http.delete(`/api/admin/settings/backgrounds/${bg.id}/`);
    customs.value = customs.value.filter((x) => x.id !== bg.id);
    if (selectedKind.value === "custom" && selectedValue.value === bg.key) {
      const fallback = builtins.value[0];
      if (fallback) {
        selectedKind.value = "builtin";
        selectedValue.value = fallback.key;
      }
    }
    ElMessage.success("已删除");
  } catch (e: any) {
    if (e === "cancel" || e === "close") return;
    ElMessage.error(e?.response?.data?.detail || "删除失败");
  }
}

async function save() {
  saving.value = true;
  try {
    const fd = new FormData();
    fd.append("company_name", companyName.value);
    if (file.value) fd.append("logo", file.value);
    fd.append("page_background_kind", selectedKind.value);
    fd.append("page_background_value", selectedValue.value);
    const { data } = await http.put("/api/admin/settings/branding/", fd, { headers: { "Content-Type": "multipart/form-data" } });
    logoUrl.value = data.logo_url;
    ElMessage.success("已保存");
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || "保存失败");
  } finally {
    saving.value = false;
  }
}

onMounted(() => load().catch(() => undefined));
</script>
