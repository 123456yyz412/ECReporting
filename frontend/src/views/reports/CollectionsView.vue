<template>
  <AppBreadcrumb :items="[{ label: '报表模块' }]" />
  <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px">
    <div class="page-title" style="font-size: 18px">报表集合（二级模块）</div>
    <el-button type="primary" @click="openCreate">新建集合</el-button>
  </div>

  <el-table :data="items" style="width: 100%" @row-click="go">
    <el-table-column prop="id" label="ID" width="80" />
    <el-table-column prop="name" label="名称" />
    <el-table-column prop="created_by_username" label="创建人" width="140" />
    <el-table-column prop="updated_at" label="更新时间" width="200" />
    <el-table-column label="操作" width="120">
      <template #default="{ row }">
        <el-button size="small" type="danger" @click.stop="removeCollection(row)">删除</el-button>
      </template>
    </el-table-column>
  </el-table>

  <el-dialog v-model="createOpen" title="新建集合" width="520px">
    <el-form label-position="top">
      <el-form-item label="名称">
        <el-input v-model="form.name" />
      </el-form-item>
      <el-form-item label="描述">
        <el-input v-model="form.description" type="textarea" :rows="3" />
      </el-form-item>
      <el-form-item v-if="auth.me?.is_admin" label="授权用户组（可选）">
        <el-select v-model="form.group_ids" multiple filterable style="width: 100%">
          <el-option v-for="g in groups" :key="g.id" :label="g.name" :value="g.id" />
        </el-select>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="createOpen = false">取消</el-button>
      <el-button type="primary" :loading="creating" @click="create">创建</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";
import { http } from "../../api/http";
import { useAuthStore } from "../../stores/auth";
import AppBreadcrumb from "../../components/AppBreadcrumb.vue";

const auth = useAuthStore();
const router = useRouter();

const items = ref<any[]>([]);
const groups = ref<any[]>([]);

const createOpen = ref(false);
const creating = ref(false);
const form = reactive<{ name: string; description: string; group_ids: number[] }>({
  name: "",
  description: "",
  group_ids: []
});

async function load() {
  const { data } = await http.get("/api/reports/collections/");
  items.value = data;
}

async function loadGroups() {
  if (!auth.me?.is_admin) return;
  const { data } = await http.get("/api/admin/groups/");
  groups.value = Array.isArray(data) ? data : data?.results || [];
}

function openCreate() {
  form.name = "";
  form.description = "";
  form.group_ids = [];
  createOpen.value = true;
}

async function create() {
  creating.value = true;
  try {
    const payload: any = { name: form.name, description: form.description };
    if (auth.me?.is_admin) payload.group_ids = form.group_ids;
    await http.post("/api/reports/collections/", payload);
    createOpen.value = false;
    await load();
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || "创建失败");
  } finally {
    creating.value = false;
  }
}

function go(row: any) {
  router.push(`/reports/collections/${row.id}`);
}

async function removeCollection(row: any) {
  try {
    await ElMessageBox.confirm(`确认删除集合“${row.name}”吗？这会同时删除其查询和看板。`, "删除集合", {
      type: "warning"
    });
    await http.delete(`/api/reports/collections/${row.id}/`);
    ElMessage.success("已删除");
    await load();
  } catch (e: any) {
    if (e === "cancel" || e === "close") return;
    ElMessage.error(e?.response?.data?.detail || "删除失败");
  }
}

onMounted(() => {
  load().catch(() => undefined);
  loadGroups().catch(() => undefined);
});
</script>
