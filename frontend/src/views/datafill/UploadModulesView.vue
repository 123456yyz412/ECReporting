<template>
  <AppBreadcrumb :items="[{ label: '数据填报' }]" />
  <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px">
    <div class="page-title" style="font-size: 18px">数据填报模块</div>
    <div style="display: flex; gap: 8px">
      <el-button @click="load">刷新</el-button>
      <el-button v-if="auth.me?.is_admin" type="primary" @click="openCreate">新建填报模块</el-button>
    </div>
  </div>

  <el-table :data="modules" style="width: 100%">
    <el-table-column prop="id" label="ID" width="80" />
    <el-table-column prop="name" label="名称" />
    <el-table-column prop="datasource_id" label="数据源ID" width="100" />
    <el-table-column prop="table_name" label="表" />
    <el-table-column label="操作" width="120" v-if="auth.me?.is_admin">
      <template #default="{ row }">
        <el-button size="small" type="danger" @click="removeModule(row)">删除</el-button>
      </template>
    </el-table-column>
    <el-table-column label="模板" width="160">
      <template #default="{ row }">
        <el-button size="small" @click="download(row.id, 'csv')">CSV</el-button>
        <el-button size="small" @click="download(row.id, 'xlsx')">XLSX</el-button>
      </template>
    </el-table-column>
    <el-table-column label="上传" width="220">
      <template #default="{ row }">
        <input type="file" accept=".csv,.xlsx" @change="(e) => onFile(row.id, e)" />
      </template>
    </el-table-column>
  </el-table>

  <el-card style="margin-top: 12px">
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px">
      <div class="page-title" style="font-size: 16px">我的上传记录</div>
      <el-button size="small" @click="loadJobs">刷新</el-button>
    </div>
    <el-table :data="jobs" size="small" style="width: 100%">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="filename" label="文件名" />
      <el-table-column prop="status" label="状态" width="100" />
      <el-table-column prop="total_rows" label="总行数" width="90" />
      <el-table-column prop="inserted_rows" label="入库行数" width="90" />
      <el-table-column prop="error" label="错误" />
      <el-table-column prop="created_at" label="时间" width="200" />
    </el-table>
  </el-card>

  <el-dialog v-model="createOpen" title="新建填报模块" width="760px">
    <el-form label-position="top">
      <el-row :gutter="12">
        <el-col :span="12">
          <el-form-item label="模块名称">
            <el-input v-model="form.name" placeholder="例如：签收信息填报" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="授权用户组">
            <el-select v-model="form.group_ids" multiple filterable style="width: 100%">
              <el-option v-for="g in groups" :key="g.id" :label="g.name" :value="g.id" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="12">
        <el-col :span="12">
          <el-form-item label="数据源实例">
            <el-select v-model="form.datasource_id" filterable style="width: 100%" @change="onDatasourceChange">
              <el-option v-for="d in datasources" :key="d.id" :label="`${d.id} - ${d.name}`" :value="d.id" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="目标表">
            <el-select
              v-model="form.table_name"
              filterable
              style="width: 100%"
              :disabled="!form.datasource_id"
              @change="onTableChange"
            >
              <el-option
                v-for="t in tables"
                :key="`${t.schema}.${t.name}`"
                :label="`${t.schema}.${t.name} (${t.type})`"
                :value="t.name"
              />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>

      <el-form-item label="字段中文名（可编辑，未填时默认取数据库注释）">
        <el-table :data="columns" size="small" style="width: 100%" max-height="280">
          <el-table-column prop="name" label="英文名" width="220" />
          <el-table-column prop="comment" label="数据库注释" width="240" />
          <el-table-column label="中文名">
            <template #default="{ row }">
              <el-input v-model="row.cn" />
            </template>
          </el-table-column>
        </el-table>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="createOpen = false">取消</el-button>
      <el-button type="primary" :loading="creating" @click="createModule">创建</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { http } from "../../api/http";
import { useAuthStore } from "../../stores/auth";
import AppBreadcrumb from "../../components/AppBreadcrumb.vue";

const auth = useAuthStore();
const modules = ref<any[]>([]);
const jobs = ref<any[]>([]);
const datasources = ref<any[]>([]);
const groups = ref<any[]>([]);
const tables = ref<any[]>([]);
const columns = ref<any[]>([]);

const createOpen = ref(false);
const creating = ref(false);
const form = reactive<any>({
  name: "",
  datasource_id: null as number | null,
  table_name: "",
  schema: "",
  group_ids: [] as number[]
});

async function load() {
  const { data } = await http.get("/api/datafill/modules/");
  modules.value = Array.isArray(data) ? data : data?.results || [];
}

async function loadJobs() {
  const { data } = await http.get("/api/datafill/jobs/");
  jobs.value = data.results || data;
}

async function loadDatasources() {
  if (!auth.me?.is_admin) return;
  const { data } = await http.get("/api/datasources/");
  datasources.value = Array.isArray(data) ? data : data?.results || [];
}

async function loadGroups() {
  if (!auth.me?.is_admin) return;
  const { data } = await http.get("/api/admin/groups/");
  groups.value = Array.isArray(data) ? data : data?.results || [];
}

function openCreate() {
  form.name = "";
  form.datasource_id = datasources.value?.[0]?.id ?? null;
  form.table_name = "";
  form.schema = "";
  form.group_ids = [];
  tables.value = [];
  columns.value = [];
  createOpen.value = true;
  if (form.datasource_id) onDatasourceChange(form.datasource_id);
}

async function onDatasourceChange(id: number) {
  if (!id) return;
  const { data } = await http.get(`/api/datasources/${id}/tables/`);
  tables.value = (data?.items || []).filter((x: any) => x.type === "table" || x.type === "view");
  form.table_name = "";
  form.schema = "";
  columns.value = [];
}

async function onTableChange(tableName: string) {
  if (!form.datasource_id || !tableName) return;
  const table = tables.value.find((t) => t.name === tableName);
  form.schema = table?.schema || "";
  const { data } = await http.get(`/api/datasources/${form.datasource_id}/columns/`, {
    params: { table: tableName, schema: form.schema }
  });
  columns.value = (data || []).map((c: any) => ({
    name: c.name,
    comment: c.comment || "",
    cn: c.comment || ""
  }));
}

async function createModule() {
  creating.value = true;
  try {
    const colMap: Record<string, string> = {};
    for (const c of columns.value) {
      if (c.cn && String(c.cn).trim()) colMap[c.name] = String(c.cn).trim();
    }
    await http.post("/api/datafill/modules/", {
      name: form.name,
      datasource_id: form.datasource_id,
      table_name: form.table_name,
      schema: form.schema,
      columns: colMap,
      group_ids: form.group_ids,
      is_active: true
    });
    createOpen.value = false;
    ElMessage.success("填报模块已创建");
    await load();
  } catch (e: any) {
    const resp = e?.response?.data;
    const msg = resp?.detail || resp?.name?.[0] || resp?.table_name?.[0] || "创建失败";
    ElMessage.error(msg);
  } finally {
    creating.value = false;
  }
}

async function removeModule(row: any) {
  try {
    await ElMessageBox.confirm(`确认删除填报模块“${row.name}”吗？`, "删除填报模块", { type: "warning" });
    await http.delete(`/api/datafill/modules/${row.id}/`);
    ElMessage.success("已删除");
    await load();
  } catch (e: any) {
    if (e === "cancel" || e === "close") return;
    ElMessage.error(e?.response?.data?.detail || "删除失败");
  }
}

function download(id: number, type: "csv" | "xlsx") {
  const url = type === "csv" ? `/api/datafill/modules/${id}/template_csv/` : `/api/datafill/modules/${id}/template_xlsx/`;
  window.open(url, "_blank");
}

async function onFile(moduleId: number, e: Event) {
  const input = e.target as HTMLInputElement;
  const file = input.files?.[0];
  if (!file) return;
  const fd = new FormData();
  fd.append("file", file);
  try {
    await http.post(`/api/datafill/modules/${moduleId}/upload/`, fd, { headers: { "Content-Type": "multipart/form-data" } });
    ElMessage.success("上传完成");
    await loadJobs();
  } catch (err: any) {
    ElMessage.error(err?.response?.data?.error || err?.response?.data?.detail || "上传失败");
  } finally {
    input.value = "";
  }
}

onMounted(() => {
  load().catch(() => undefined);
  loadJobs().catch(() => undefined);
  loadDatasources().catch(() => undefined);
  loadGroups().catch(() => undefined);
});
</script>
