<template>
  <AppBreadcrumb :items="breadcrumbItems" />
  <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px">
    <div class="page-title" style="font-size: 18px">看板：{{ dashboard?.name }}</div>
    <div style="display: flex; gap: 8px">
      <el-button type="danger" plain @click="removeDashboard">删除</el-button>
      <el-button @click="load">刷新</el-button>
      <el-button type="primary" :loading="saving" @click="save">保存</el-button>
      <el-button type="success" @click="toggleEdit">{{ editing ? "预览" : "编辑" }}</el-button>
    </div>
  </div>

  <el-row :gutter="12">
    <el-col :span="6">
      <el-card>
        <el-form label-position="top">
          <el-form-item label="名称">
            <el-input v-model="form.name" />
          </el-form-item>
          <el-form-item label="布局模式">
            <el-select v-model="form.layout_mode" style="width: 100%">
              <el-option label="大屏模式" value="screen" />
              <el-option label="PDF页面布局" value="pdf" />
            </el-select>
          </el-form-item>
          <el-form-item label="背景色">
            <el-color-picker v-model="form.background.color" />
          </el-form-item>
          <el-form-item label="背景图片URL（可选）">
            <el-input v-model="form.background.imageUrl" />
          </el-form-item>
        </el-form>

        <div style="display: flex; align-items: center; justify-content: space-between; margin-top: 10px">
          <div style="font-weight: 600">组件</div>
          <el-button size="small" type="primary" :disabled="!editing" @click="openAdd">添加</el-button>
        </div>
        <el-table :data="widgets" size="small" style="width: 100%; margin-top: 8px">
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="queryId" label="查询" width="80" />
          <el-table-column prop="visType" label="图表" />
          <el-table-column label="操作" width="90">
            <template #default="{ row }">
              <el-button size="small" text type="danger" :disabled="!editing" @click="removeWidget(row.id)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </el-col>
    <el-col :span="18">
      <el-card>
        <div
          ref="canvas"
          :style="canvasStyle"
          style="position: relative; overflow: hidden; border: 1px dashed #ddd"
        >
          <div
            v-for="w in widgets"
            :key="w.id"
            class="widget"
            :data-id="w.id"
            :style="widgetStyle(w)"
          >
            <div style="position: absolute; top: 6px; left: 8px; z-index: 2; font-weight: 600">
              #{{ w.queryId }}
            </div>
            <div style="position: absolute; inset: 0; padding-top: 26px">
              <div v-if="w.visType === 'table'" style="height: 100%">
                <el-table :data="results[w.queryId]?.rows || []" style="width: 100%" height="100%">
                  <el-table-column
                    v-for="c in results[w.queryId]?.columns || []"
                    :key="c"
                    :prop="c"
                    :label="c"
                  />
                </el-table>
              </div>
              <div v-else style="height: 100%">
                <ChartRenderer
                  :type="w.visType"
                  :rows="results[w.queryId]?.rows || []"
                  :config="w.config || {}"
                />
              </div>
            </div>
          </div>
        </div>
      </el-card>
    </el-col>
  </el-row>

  <el-dialog v-model="addOpen" title="添加组件" width="520px">
    <el-form label-position="top">
      <el-form-item label="选择查询">
        <el-select v-model="addForm.queryId" filterable style="width: 100%">
          <el-option v-for="q in queries" :key="q.id" :label="`${q.id} - ${q.name}`" :value="q.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="图表类型">
        <el-select v-model="addForm.visType" style="width: 100%">
          <el-option label="数据表" value="table" />
          <el-option label="柱状图" value="bar" />
          <el-option label="折线图" value="line" />
          <el-option label="面积图" value="area" />
          <el-option label="饼图" value="pie" />
          <el-option label="散点图" value="scatter" />
        </el-select>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="addOpen = false">取消</el-button>
      <el-button type="primary" @click="addWidget">添加</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import interact from "interactjs";
import { computed, nextTick, onMounted, reactive, ref, watch } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { useRouter } from "vue-router";
import { http } from "../../api/http";
import ChartRenderer from "../../components/ChartRenderer.vue";
import AppBreadcrumb from "../../components/AppBreadcrumb.vue";

type Widget = {
  id: string;
  queryId: number;
  visType: string;
  config?: Record<string, any>;
  x: number;
  y: number;
  w: number;
  h: number;
};

const props = defineProps<{ id: string }>();
const router = useRouter();

const dashboard = ref<any | null>(null);
const queries = ref<any[]>([]);
const results = reactive<Record<number, any>>({});
const saving = ref(false);
const editing = ref(false);

const form = reactive<any>({
  name: "",
  layout_mode: "screen",
  background: { color: "#ffffff", imageUrl: "" },
  definition: { widgets: [] as Widget[] }
});

const widgets = computed<Widget[]>(() => form.definition.widgets || []);

const canvas = ref<HTMLDivElement | null>(null);

const breadcrumbItems = computed(() => [
  { label: "报表模块", to: "/reports" },
  dashboard.value?.collection
    ? { label: dashboard.value?.collection_name || `集合 ${dashboard.value.collection}`, to: `/reports/collections/${dashboard.value.collection}` }
    : { label: "集合" },
  { label: dashboard.value?.name || `看板 ${props.id}` }
]);

const canvasStyle = computed(() => {
  const bg = form.background || {};
  const size =
    form.layout_mode === "pdf"
      ? { width: "900px", height: "1200px" }
      : { width: "100%", height: "800px" };
  return {
    ...size,
    backgroundColor: bg.color || "#fff",
    backgroundImage: bg.imageUrl ? `url(${bg.imageUrl})` : "",
    backgroundSize: "cover",
    backgroundPosition: "center"
  } as any;
});

function widgetStyle(w: Widget) {
  return {
    position: "absolute",
    left: `${w.x}px`,
    top: `${w.y}px`,
    width: `${w.w}px`,
    height: `${w.h}px`,
    background: "rgba(255,255,255,0.92)",
    border: "1px solid #ddd",
    borderRadius: "4px",
    boxSizing: "border-box",
    overflow: "hidden"
  };
}

async function load() {
  const { data } = await http.get(`/api/reports/dashboards/${props.id}/`);
  dashboard.value = data;
  form.name = data.name;
  form.layout_mode = data.layout_mode || "screen";
  form.background = data.background || { color: "#ffffff", imageUrl: "" };
  form.definition = data.definition || { widgets: [] };

  const q = await http.get(`/api/reports/queries/?collection=${data.collection}`);
  queries.value = q.data;
  await runAll();
  await nextTick();
  bindInteract();
}

async function runAll() {
  const ids = new Set<number>();
  for (const w of widgets.value) ids.add(w.queryId);
  await Promise.all(
    Array.from(ids).map(async (id) => {
      const { data } = await http.post(`/api/reports/queries/${id}/run/`, { params: {} });
      results[id] = data;
    })
  );
}

async function save() {
  saving.value = true;
  try {
    const payload = {
      collection: dashboard.value.collection,
      name: form.name,
      layout_mode: form.layout_mode,
      background: form.background,
      definition: form.definition
    };
    await http.put(`/api/reports/dashboards/${props.id}/`, payload);
    ElMessage.success("已保存");
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || "保存失败");
  } finally {
    saving.value = false;
  }
}

async function removeDashboard() {
  try {
    await ElMessageBox.confirm(`确认删除看板“${dashboard.value?.name || ""}”吗？`, "删除看板", { type: "warning" });
    const collectionId = dashboard.value?.collection;
    await http.delete(`/api/reports/dashboards/${props.id}/`);
    ElMessage.success("已删除");
    if (collectionId) router.push(`/reports/collections/${collectionId}`);
    else router.push("/reports");
  } catch (e: any) {
    if (e === "cancel" || e === "close") return;
    ElMessage.error(e?.response?.data?.detail || "删除失败");
  }
}

function toggleEdit() {
  editing.value = !editing.value;
  nextTick().then(bindInteract);
}

const addOpen = ref(false);
const addForm = reactive<{ queryId: number | null; visType: string }>({ queryId: null, visType: "table" });

function openAdd() {
  addForm.queryId = queries.value?.[0]?.id ?? null;
  addForm.visType = "table";
  addOpen.value = true;
}

function addWidget() {
  if (!addForm.queryId) return;
  const id = String(Date.now());
  const w: Widget = { id, queryId: addForm.queryId, visType: addForm.visType, x: 20, y: 20, w: 420, h: 260 };
  form.definition.widgets = [...widgets.value, w];
  addOpen.value = false;
  runAll().catch(() => undefined);
  nextTick().then(bindInteract);
}

function removeWidget(id: string) {
  form.definition.widgets = widgets.value.filter((w) => w.id !== id);
  nextTick().then(bindInteract);
}

function bindInteract() {
  if (!canvas.value) return;
  interact(".widget").unset();
  if (!editing.value) return;
  interact(".widget")
    .draggable({
      listeners: {
        move(event) {
          const target = event.target as HTMLElement;
          const id = target.getAttribute("data-id");
          if (!id) return;
          const w = widgets.value.find((x) => x.id === id);
          if (!w) return;
          w.x += event.dx;
          w.y += event.dy;
        }
      }
    })
    .resizable({
      edges: { left: true, right: true, bottom: true, top: true },
      listeners: {
        move(event) {
          const target = event.target as HTMLElement;
          const id = target.getAttribute("data-id");
          if (!id) return;
          const w = widgets.value.find((x) => x.id === id);
          if (!w) return;
          w.x += event.deltaRect.left;
          w.y += event.deltaRect.top;
          w.w = Math.max(120, w.w + event.deltaRect.width);
          w.h = Math.max(80, w.h + event.deltaRect.height);
        }
      }
    });
}

watch(
  () => widgets.value.length,
  () => nextTick().then(bindInteract)
);

onMounted(() => {
  load().catch((e) => ElMessage.error(e?.response?.data?.detail || "加载失败"));
});
</script>
