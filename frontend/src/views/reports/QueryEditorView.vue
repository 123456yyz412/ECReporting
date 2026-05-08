<template>
  <AppBreadcrumb :items="breadcrumbItems" />
  <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px">
    <div class="page-title" style="font-size: 18px">查询：{{ query?.name }}</div>
    <div style="display: flex; gap: 8px">
      <el-button type="danger" plain @click="removeQuery">删除</el-button>
      <el-button @click="load">刷新</el-button>
      <el-button type="primary" :loading="saving" @click="save">保存</el-button>
      <el-button type="success" :loading="running" @click="run">运行</el-button>
    </div>
  </div>

  <el-row :gutter="12">
    <el-col :span="12">
      <el-card>
        <el-form label-position="top">
          <el-form-item label="名称">
            <el-input v-model="form.name" />
          </el-form-item>
          <el-form-item label="隐藏SQL">
            <el-switch v-model="form.is_hidden" />
          </el-form-item>
          <el-form-item label="SQL">
            <el-input
              v-model="form.sql_text"
              type="textarea"
              :rows="12"
              :disabled="query && query.sql_text === null"
              placeholder="仅允许SELECT/WITH"
            />
          </el-form-item>
        </el-form>
        <div v-if="query && query.sql_text === null" style="color: #999">该查询SQL已被隐藏，你没有查看/编辑权限。</div>
      </el-card>
    </el-col>
    <el-col :span="12">
      <el-card>
        <el-form label-position="top">
          <el-form-item label="可视化类型">
            <el-select v-model="form.visualization_type" style="width: 100%">
              <el-option label="数据表" value="table" />
              <el-option label="柱状图" value="bar" />
              <el-option label="折线图" value="line" />
              <el-option label="面积图" value="area" />
              <el-option label="饼图" value="pie" />
              <el-option label="散点图" value="scatter" />
            </el-select>
          </el-form-item>
          <el-form-item v-if="form.visualization_type !== 'table'" label="X字段">
            <el-input v-model="form.visualization_config.xField" placeholder="例如：date" />
          </el-form-item>
          <el-form-item v-if="form.visualization_type !== 'table' && form.visualization_type !== 'scatter'" label="Y字段">
            <el-input v-model="form.visualization_config.yField" placeholder="例如：amount" />
          </el-form-item>
          <el-form-item v-if="form.visualization_type === 'scatter'" label="X数值字段">
            <el-input v-model="form.visualization_config.x2Field" />
          </el-form-item>
          <el-form-item v-if="form.visualization_type === 'scatter'" label="Y数值字段">
            <el-input v-model="form.visualization_config.y2Field" />
          </el-form-item>
        </el-form>
      </el-card>
    </el-col>
  </el-row>

  <el-card style="margin-top: 12px">
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px">
      <div style="font-size: 16px; font-weight: 600">结果预览</div>
      <div v-if="result.truncated" style="color: #e6a23c">结果已截断（最多5000行）</div>
    </div>

    <div v-if="form.visualization_type === 'table'">
      <el-table :data="result.rows" style="width: 100%" height="480">
        <el-table-column v-for="c in result.columns" :key="c" :prop="c" :label="c" />
      </el-table>
    </div>
    <div v-else style="height: 520px">
      <ChartRenderer :type="form.visualization_type" :rows="result.rows" :config="form.visualization_config" />
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { useRouter } from "vue-router";
import { http } from "../../api/http";
import ChartRenderer from "../../components/ChartRenderer.vue";
import AppBreadcrumb from "../../components/AppBreadcrumb.vue";

const props = defineProps<{ id: string }>();
const router = useRouter();

const query = ref<any | null>(null);
const saving = ref(false);
const running = ref(false);

const form = reactive<any>({
  name: "",
  sql_text: "",
  is_hidden: false,
  visualization_type: "table",
  visualization_config: {}
});

const result = reactive<{ columns: string[]; rows: any[]; truncated: boolean }>({
  columns: [],
  rows: [],
  truncated: false
});

const breadcrumbItems = computed(() => [
  { label: "报表模块", to: "/reports" },
  query.value?.collection
    ? { label: query.value?.collection_name || `集合 ${query.value.collection}`, to: `/reports/collections/${query.value.collection}` }
    : { label: "集合" },
  { label: query.value?.name || `查询 ${props.id}` }
]);

async function load() {
  const { data } = await http.get(`/api/reports/queries/${props.id}/`);
  query.value = data;
  form.name = data.name;
  form.sql_text = data.sql_text ?? "";
  form.is_hidden = data.is_hidden;
  form.visualization_type = data.visualization_type || "table";
  form.visualization_config = data.visualization_config || {};
}

async function save() {
  saving.value = true;
  try {
    const payload: any = {
      collection: query.value.collection,
      datasource_id: query.value.datasource_id,
      name: form.name,
      is_hidden: form.is_hidden,
      visualization_type: form.visualization_type,
      visualization_config: form.visualization_config
    };
    if (query.value.sql_text !== null) payload.sql_text = form.sql_text;
    const { data } = await http.put(`/api/reports/queries/${props.id}/`, payload);
    query.value = data;
    ElMessage.success("已保存");
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || "保存失败");
  } finally {
    saving.value = false;
  }
}

async function run() {
  running.value = true;
  try {
    const { data } = await http.post(`/api/reports/queries/${props.id}/run/`, { params: {} });
    result.columns = data.columns;
    result.rows = data.rows;
    result.truncated = data.truncated;
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || e?.response?.data?.error || "运行失败");
  } finally {
    running.value = false;
  }
}

async function removeQuery() {
  try {
    await ElMessageBox.confirm(`确认删除查询“${query.value?.name || ""}”吗？`, "删除查询", { type: "warning" });
    const collectionId = query.value?.collection;
    await http.delete(`/api/reports/queries/${props.id}/`);
    ElMessage.success("已删除");
    if (collectionId) router.push(`/reports/collections/${collectionId}`);
    else router.push("/reports");
  } catch (e: any) {
    if (e === "cancel" || e === "close") return;
    ElMessage.error(e?.response?.data?.detail || "删除失败");
  }
}

onMounted(() => {
  load().then(run).catch((e) => ElMessage.error(e?.response?.data?.detail || "加载失败"));
});
</script>
