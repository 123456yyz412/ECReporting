<template>
  <AppBreadcrumb :items="breadcrumbItems" />
  <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px">
    <div class="page-title" style="font-size: 18px">集合：{{ collection?.name }}</div>
    <div style="display: flex; gap: 8px">
      <el-button type="danger" plain @click="removeCollection">删除集合</el-button>
      <el-button @click="load">刷新</el-button>
      <el-button type="primary" @click="openCreateQuery">新建查询</el-button>
      <el-button type="primary" plain @click="openCreateDashboard">新建看板</el-button>
    </div>
  </div>

  <el-tabs v-model="tab">
    <el-tab-pane name="dashboards" label="看板">
      <el-table :data="dashboards" style="width: 100%" @row-click="goDashboard">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="layout_mode" label="布局" width="120" />
        <el-table-column prop="updated_at" label="更新时间" width="200" />
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button size="small" type="danger" @click.stop="removeDashboard(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-tab-pane>
    <el-tab-pane name="queries" label="查询">
      <el-table :data="queries" style="width: 100%" @row-click="goQuery">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="is_hidden" label="隐藏SQL" width="120">
          <template #default="{ row }">
            <el-tag v-if="row.is_hidden" type="warning">隐藏</el-tag>
            <el-tag v-else type="success">可见</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="visualization_type" label="可视化" width="120" />
        <el-table-column prop="updated_at" label="更新时间" width="200" />
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button size="small" type="danger" @click.stop="removeQuery(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-tab-pane>
  </el-tabs>

  <el-dialog v-model="createQueryOpen" title="新建查询" width="760px">
    <el-form label-position="top">
      <el-form-item label="名称">
        <el-input v-model="qform.name" />
      </el-form-item>
      <el-form-item label="数据源">
        <el-select v-model="qform.datasource_id" filterable style="width: 100%">
          <el-option v-for="d in datasources" :key="d.id" :label="d.name" :value="d.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="SQL（仅允许SELECT/WITH）">
        <el-input v-model="qform.sql_text" type="textarea" :rows="8" />
      </el-form-item>
      <el-form-item label="隐藏SQL">
        <el-switch v-model="qform.is_hidden" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="createQueryOpen = false">取消</el-button>
      <el-button type="primary" :loading="creatingQuery" @click="createQuery">创建</el-button>
    </template>
  </el-dialog>

  <el-dialog v-model="createDashboardOpen" title="新建看板" width="520px">
    <el-form label-position="top">
      <el-form-item label="名称">
        <el-input v-model="dform.name" />
      </el-form-item>
      <el-form-item label="布局模式">
        <el-select v-model="dform.layout_mode" style="width: 100%">
          <el-option label="大屏模式" value="screen" />
          <el-option label="PDF页面布局" value="pdf" />
        </el-select>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="createDashboardOpen = false">取消</el-button>
      <el-button type="primary" :loading="creatingDashboard" @click="createDashboard">创建</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";
import { http } from "../../api/http";
import AppBreadcrumb from "../../components/AppBreadcrumb.vue";

const props = defineProps<{ id: string }>();
const router = useRouter();

const tab = ref("dashboards");
const collection = ref<any | null>(null);
const queries = ref<any[]>([]);
const dashboards = ref<any[]>([]);
const datasources = ref<any[]>([]);

const createQueryOpen = ref(false);
const creatingQuery = ref(false);
const qform = reactive<any>({
  name: "",
  datasource_id: null as number | null,
  sql_text: "",
  is_hidden: false
});

const createDashboardOpen = ref(false);
const creatingDashboard = ref(false);
const dform = reactive<any>({ name: "", layout_mode: "screen" });

const breadcrumbItems = computed(() => [
  { label: "报表模块", to: "/reports" },
  { label: collection.value?.name || `集合 ${props.id}` }
]);

async function load() {
  const { data } = await http.get(`/api/reports/collections/${props.id}/`);
  collection.value = data;
  const q = await http.get(`/api/reports/queries/?collection=${props.id}`);
  queries.value = q.data;
  const d = await http.get(`/api/reports/dashboards/?collection=${props.id}`);
  dashboards.value = d.data;
}

async function loadDatasources() {
  const { data } = await http.get("/api/datasources/");
  datasources.value = data;
}

function openCreateQuery() {
  qform.name = "";
  qform.datasource_id = datasources.value?.[0]?.id ?? null;
  qform.sql_text = "";
  qform.is_hidden = false;
  createQueryOpen.value = true;
}

async function createQuery() {
  creatingQuery.value = true;
  try {
    const payload = {
      collection: Number(props.id),
      datasource_id: qform.datasource_id,
      name: qform.name,
      sql_text: qform.sql_text,
      is_hidden: qform.is_hidden,
      visualization_type: "table",
      visualization_config: {}
    };
    const { data } = await http.post("/api/reports/queries/", payload);
    createQueryOpen.value = false;
    router.push(`/reports/queries/${data.id}`);
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || "创建失败");
  } finally {
    creatingQuery.value = false;
  }
}

function openCreateDashboard() {
  dform.name = "";
  dform.layout_mode = "screen";
  createDashboardOpen.value = true;
}

async function createDashboard() {
  creatingDashboard.value = true;
  try {
    const payload = {
      collection: Number(props.id),
      name: dform.name,
      layout_mode: dform.layout_mode,
      background: {},
      definition: { widgets: [], filters: [] }
    };
    const { data } = await http.post("/api/reports/dashboards/", payload);
    createDashboardOpen.value = false;
    router.push(`/reports/dashboards/${data.id}`);
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || "创建失败");
  } finally {
    creatingDashboard.value = false;
  }
}

function goQuery(row: any) {
  router.push(`/reports/queries/${row.id}`);
}

function goDashboard(row: any) {
  router.push(`/reports/dashboards/${row.id}`);
}

async function removeCollection() {
  try {
    await ElMessageBox.confirm(`确认删除集合“${collection.value?.name || ""}”吗？这会同时删除其查询和看板。`, "删除集合", {
      type: "warning"
    });
    await http.delete(`/api/reports/collections/${props.id}/`);
    ElMessage.success("已删除");
    router.push("/reports");
  } catch (e: any) {
    if (e === "cancel" || e === "close") return;
    ElMessage.error(e?.response?.data?.detail || "删除失败");
  }
}

async function removeQuery(row: any) {
  try {
    await ElMessageBox.confirm(`确认删除查询“${row.name}”吗？`, "删除查询", { type: "warning" });
    await http.delete(`/api/reports/queries/${row.id}/`);
    ElMessage.success("已删除");
    await load();
  } catch (e: any) {
    if (e === "cancel" || e === "close") return;
    ElMessage.error(e?.response?.data?.detail || "删除失败");
  }
}

async function removeDashboard(row: any) {
  try {
    await ElMessageBox.confirm(`确认删除看板“${row.name}”吗？`, "删除看板", { type: "warning" });
    await http.delete(`/api/reports/dashboards/${row.id}/`);
    ElMessage.success("已删除");
    await load();
  } catch (e: any) {
    if (e === "cancel" || e === "close") return;
    ElMessage.error(e?.response?.data?.detail || "删除失败");
  }
}

onMounted(() => {
  loadDatasources().catch(() => undefined);
  load().catch((e) => ElMessage.error(e?.response?.data?.detail || "加载失败"));
});
</script>
