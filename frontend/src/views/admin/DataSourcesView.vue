<template>
  <AppBreadcrumb :items="breadcrumbItems" />
  <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px">
    <div class="page-title" style="font-size: 18px">数据源实例</div>
    <el-button type="primary" @click="openCreate">新建</el-button>
  </div>

  <el-table :data="items" style="width: 100%">
    <el-table-column prop="id" label="ID" width="80" />
    <el-table-column prop="name" label="名称" />
    <el-table-column prop="db_type" label="类型" width="120" />
    <el-table-column prop="host" label="Host" />
    <el-table-column prop="port" label="Port" width="90" />
    <el-table-column prop="database" label="DB" />
    <el-table-column prop="schema" label="Schema" />
    <el-table-column label="操作" width="220">
      <template #default="{ row }">
        <el-button size="small" @click="test(row.id)">测试</el-button>
        <el-button size="small" @click="showTables(row.id)">表/视图</el-button>
        <el-button size="small" type="danger" @click="removeDataSource(row)">删除</el-button>
      </template>
    </el-table-column>
  </el-table>

  <el-dialog v-model="createOpen" title="新建数据源实例" width="640px">
    <el-form label-position="top">
      <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
      <el-form-item label="类型">
        <el-select v-model="form.db_type" style="width: 100%">
          <el-option label="PostgreSQL" value="postgres" />
          <el-option label="MySQL" value="mysql" />
        </el-select>
      </el-form-item>
      <el-row :gutter="12">
        <el-col :span="12"><el-form-item label="Host"><el-input v-model="form.host" /></el-form-item></el-col>
        <el-col :span="12"><el-form-item label="Port"><el-input v-model="form.port" /></el-form-item></el-col>
      </el-row>
      <el-row :gutter="12">
        <el-col :span="12"><el-form-item label="Database"><el-input v-model="form.database" /></el-form-item></el-col>
        <el-col :span="12"><el-form-item label="Schema（Postgres可选）"><el-input v-model="form.schema" /></el-form-item></el-col>
      </el-row>
      <el-row :gutter="12">
        <el-col :span="12"><el-form-item label="Username"><el-input v-model="form.username" /></el-form-item></el-col>
        <el-col :span="12"><el-form-item label="Password"><el-input v-model="form.password" type="password" show-password /></el-form-item></el-col>
      </el-row>
    </el-form>
    <template #footer>
      <el-button @click="createOpen = false">取消</el-button>
      <el-button type="primary" :loading="creating" @click="create">创建</el-button>
    </template>
  </el-dialog>

  <el-dialog v-model="tablesOpen" title="表/视图" width="700px">
    <el-table :data="tables" size="small" style="width: 100%">
      <el-table-column prop="type" label="类型" width="100" />
      <el-table-column prop="name" label="名称" />
    </el-table>
  </el-dialog>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { http } from "../../api/http";
import AppBreadcrumb from "../../components/AppBreadcrumb.vue";

const items = ref<any[]>([]);
const createOpen = ref(false);
const creating = ref(false);
const breadcrumbItems = [
  { label: "管理员", to: "/admin" },
  { label: "数据源实例" }
];

const form = reactive<any>({
  name: "",
  db_type: "postgres",
  host: "127.0.0.1",
  port: 5432,
  database: "",
  schema: "public",
  username: "",
  password: ""
});

const tablesOpen = ref(false);
const tables = ref<any[]>([]);

async function load() {
  const { data } = await http.get("/api/datasources/");
  items.value = data;
}

function openCreate() {
  form.name = "";
  form.db_type = "postgres";
  form.host = "127.0.0.1";
  form.port = 5432;
  form.database = "";
  form.schema = "public";
  form.username = "";
  form.password = "";
  createOpen.value = true;
}

async function create() {
  creating.value = true;
  try {
    await http.post("/api/datasources/", {
      name: form.name,
      db_type: form.db_type,
      host: form.host,
      port: Number(form.port),
      database: form.database,
      schema: form.schema,
      username: form.username,
      password: form.password,
      is_active: true
    });
    createOpen.value = false;
    await load();
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || "创建失败");
  } finally {
    creating.value = false;
  }
}

async function test(id: number) {
  try {
    const { data } = await http.post(`/api/datasources/${id}/test_connection/`);
    if (data.ok) ElMessage.success("连接成功");
    else ElMessage.error("连接失败");
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.error || "连接失败");
  }
}

async function showTables(id: number) {
  try {
    const { data } = await http.get(`/api/datasources/${id}/tables/`);
    tables.value = data.items || [];
    tablesOpen.value = true;
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || "加载失败");
  }
}

async function removeDataSource(row: any) {
  try {
    await ElMessageBox.confirm(`确认删除数据源“${row.name}”吗？`, "删除数据源", { type: "warning" });
    await http.delete(`/api/datasources/${row.id}/`);
    ElMessage.success("已删除");
    await load();
  } catch (e: any) {
    if (e === "cancel" || e === "close") return;
    ElMessage.error(e?.response?.data?.detail || "删除失败");
  }
}

onMounted(() => load().catch(() => undefined));
</script>
