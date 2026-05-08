<template>
  <AppBreadcrumb :items="breadcrumbItems" />
  <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px">
    <div class="page-title" style="font-size: 18px">用户组管理</div>
    <el-button type="primary" @click="openCreate">新建用户组</el-button>
  </div>

  <el-table :data="items" style="width: 100%">
    <el-table-column prop="id" label="ID" width="80" />
    <el-table-column prop="name" label="名称" />
    <el-table-column prop="user_count" label="人数" width="100" />
    <el-table-column label="操作" width="120">
      <template #default="{ row }">
        <el-button size="small" type="danger" @click="removeGroup(row)">删除</el-button>
      </template>
    </el-table-column>
  </el-table>

  <el-dialog v-model="open" title="新建用户组" width="420px">
    <el-form label-position="top">
      <el-form-item label="名称">
        <el-input v-model="name" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="open = false">取消</el-button>
      <el-button type="primary" :loading="saving" @click="create">创建</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { http } from "../../api/http";
import AppBreadcrumb from "../../components/AppBreadcrumb.vue";

const items = ref<any[]>([]);
const open = ref(false);
const name = ref("");
const saving = ref(false);
const breadcrumbItems = [
  { label: "管理员", to: "/admin" },
  { label: "用户组管理" }
];

async function load() {
  const { data } = await http.get("/api/admin/groups/");
  items.value = Array.isArray(data) ? data : data?.results || [];
}

function openCreate() {
  name.value = "";
  open.value = true;
}

async function create() {
  saving.value = true;
  try {
    await http.post("/api/admin/groups/", { name: name.value });
    open.value = false;
    await load();
  } catch (e: any) {
    const resp = e?.response?.data;
    const msg = resp?.detail || resp?.name?.[0] || "创建失败";
    ElMessage.error(msg);
  } finally {
    saving.value = false;
  }
}

async function removeGroup(row: any) {
  try {
    await ElMessageBox.confirm(`确认删除用户组“${row.name}”吗？`, "删除用户组", { type: "warning" });
    await http.delete(`/api/admin/groups/${row.id}/`);
    ElMessage.success("已删除");
    await load();
  } catch (e: any) {
    if (e === "cancel" || e === "close") return;
    const resp = e?.response?.data;
    ElMessage.error(resp?.detail || "删除失败");
  }
}

onMounted(() => load().catch(() => undefined));
</script>
