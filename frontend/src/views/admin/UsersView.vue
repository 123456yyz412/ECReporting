<template>
  <AppBreadcrumb :items="breadcrumbItems" />
  <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px">
    <div class="page-title" style="font-size: 18px">用户管理</div>
    <el-button type="primary" @click="openCreate">新建用户</el-button>
  </div>

  <el-table :data="items" style="width: 100%">
    <el-table-column prop="id" label="ID" width="80" />
    <el-table-column prop="username" label="用户名" />
    <el-table-column prop="is_admin" label="管理员" width="100">
      <template #default="{ row }">
        <el-tag v-if="row.is_admin" type="success">是</el-tag>
        <el-tag v-else>否</el-tag>
      </template>
    </el-table-column>
    <el-table-column prop="groups" label="用户组" />
    <el-table-column label="操作" width="220">
      <template #default="{ row }">
        <el-button size="small" @click="openEdit(row)">编辑</el-button>
        <el-button size="small" type="warning" @click="openReset(row)">重置密码</el-button>
        <el-button size="small" type="danger" @click="removeUser(row)">删除</el-button>
      </template>
    </el-table-column>
  </el-table>

  <el-dialog v-model="editOpen" :title="editMode === 'create' ? '新建用户' : '编辑用户'" width="600px">
    <el-form label-position="top">
      <el-form-item label="用户名" v-if="editMode === 'create'">
        <el-input v-model="form.username" />
      </el-form-item>
      <el-form-item label="密码" v-if="editMode === 'create'">
        <el-input v-model="form.password" type="password" show-password />
      </el-form-item>
      <el-form-item label="邮箱"><el-input v-model="form.email" /></el-form-item>
      <el-form-item label="启用"><el-switch v-model="form.is_active" /></el-form-item>
      <el-form-item label="管理员（is_staff）"><el-switch v-model="form.is_staff" /></el-form-item>
      <el-form-item label="用户组">
        <el-select v-model="form.group_ids" multiple filterable style="width: 100%">
          <el-option v-for="g in groups" :key="g.id" :label="g.name" :value="g.id" />
        </el-select>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="editOpen = false">取消</el-button>
      <el-button type="primary" :loading="saving" @click="save">{{ editMode === 'create' ? '创建' : '保存' }}</el-button>
    </template>
  </el-dialog>

  <el-dialog v-model="resetOpen" title="重置密码" width="420px">
    <el-form label-position="top">
      <el-form-item label="新密码">
        <el-input v-model="resetPassword" type="password" show-password />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="resetOpen = false">取消</el-button>
      <el-button type="primary" :loading="saving" @click="reset">确认</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { http } from "../../api/http";
import AppBreadcrumb from "../../components/AppBreadcrumb.vue";

const items = ref<any[]>([]);
const groups = ref<any[]>([]);
const breadcrumbItems = [
  { label: "管理员", to: "/admin" },
  { label: "用户管理" }
];

const editOpen = ref(false);
const resetOpen = ref(false);
const saving = ref(false);
const editMode = ref<"create" | "edit">("create");
const editingId = ref<number | null>(null);
const resetId = ref<number | null>(null);

const form = reactive<any>({
  username: "",
  password: "",
  email: "",
  is_active: true,
  is_staff: false,
  group_ids: [] as number[]
});

const resetPassword = ref("");

function parseError(e: any, fallback: string) {
  const resp = e?.response?.data;
  if (!resp) return fallback;
  if (typeof resp === "string") return resp;
  if (resp.detail) return resp.detail;
  const firstKey = Object.keys(resp)[0];
  const firstVal = firstKey ? resp[firstKey] : null;
  if (Array.isArray(firstVal) && firstVal.length) return String(firstVal[0]);
  if (typeof firstVal === "string") return firstVal;
  return fallback;
}

async function load() {
  const { data } = await http.get("/api/admin/users/");
  items.value = data;
}

async function loadGroups() {
  const { data } = await http.get("/api/admin/groups/");
  groups.value = Array.isArray(data) ? data : data?.results || [];
}

function openCreate() {
  editMode.value = "create";
  editingId.value = null;
  form.username = "";
  form.password = "";
  form.email = "";
  form.is_active = true;
  form.is_staff = false;
  form.group_ids = groups.value.some((g) => g.name === "普通用户")
    ? [groups.value.find((g) => g.name === "普通用户").id]
    : [];
  editOpen.value = true;
}

function openEdit(row: any) {
  editMode.value = "edit";
  editingId.value = row.id;
  form.email = row.email || "";
  form.is_active = row.is_active;
  form.is_staff = row.is_admin;
  form.group_ids = row.group_ids || [];
  editOpen.value = true;
}

async function save() {
  saving.value = true;
  try {
    if (editMode.value === "create") {
      await http.post("/api/admin/users/", {
        username: form.username,
        password: form.password,
        email: form.email,
        is_active: form.is_active,
        is_staff: form.is_staff,
        group_ids: form.group_ids
      });
    } else if (editingId.value) {
      await http.put(`/api/admin/users/${editingId.value}/`, {
        email: form.email,
        is_active: form.is_active,
        is_staff: form.is_staff,
        group_ids: form.group_ids
      });
    }
    editOpen.value = false;
    await load();
  } catch (e: any) {
    ElMessage.error(parseError(e, "保存失败"));
  } finally {
    saving.value = false;
  }
}

function openReset(row: any) {
  resetId.value = row.id;
  resetPassword.value = "";
  resetOpen.value = true;
}

async function reset() {
  if (!resetId.value) return;
  saving.value = true;
  try {
    await http.post(`/api/admin/users/${resetId.value}/reset_password/`, { password: resetPassword.value });
    resetOpen.value = false;
    ElMessage.success("已重置");
  } catch (e: any) {
    ElMessage.error(parseError(e, "重置失败"));
  } finally {
    saving.value = false;
  }
}

async function removeUser(row: any) {
  try {
    await ElMessageBox.confirm(`确认删除用户“${row.username}”吗？`, "删除用户", { type: "warning" });
    await http.delete(`/api/admin/users/${row.id}/`);
    ElMessage.success("已删除");
    await load();
  } catch (e: any) {
    if (e === "cancel" || e === "close") return;
    ElMessage.error(parseError(e, "删除失败"));
  }
}

onMounted(() => {
  load().catch(() => undefined);
  loadGroups().catch(() => undefined);
});
</script>
