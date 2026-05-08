<template>
  <div ref="el" style="width: 100%; height: 100%" />
</template>

<script setup lang="ts">
import * as echarts from "echarts";
import { onBeforeUnmount, onMounted, watch, ref } from "vue";

type DataRow = Record<string, any>;

const props = defineProps<{
  type: string;
  rows: DataRow[];
  config?: Record<string, any>;
}>();

const el = ref<HTMLDivElement | null>(null);
let chart: echarts.ECharts | null = null;

function buildOption() {
  const type = props.type || "bar";
  const rows = props.rows || [];
  const cfg = props.config || {};
  const fields = rows.length ? Object.keys(rows[0]) : [];
  const xField = cfg.xField || fields[0];
  const yField = cfg.yField || fields.find((f) => f !== xField) || fields[1];

  const xData = rows.map((r) => r?.[xField]);
  const yData = rows.map((r) => Number(r?.[yField] ?? 0));

  if (type === "pie") {
    return {
      tooltip: { trigger: "item" },
      series: [
        {
          type: "pie",
          radius: "60%",
          data: rows.map((r) => ({ name: r?.[xField], value: Number(r?.[yField] ?? 0) }))
        }
      ]
    };
  }

  if (type === "scatter") {
    const x2 = cfg.x2Field || xField;
    const y2 = cfg.y2Field || yField;
    return {
      tooltip: { trigger: "item" },
      xAxis: { type: "value" },
      yAxis: { type: "value" },
      series: [
        {
          type: "scatter",
          data: rows.map((r) => [Number(r?.[x2] ?? 0), Number(r?.[y2] ?? 0)])
        }
      ]
    };
  }

  const seriesType = type === "area" ? "line" : type;
  const areaStyle = type === "area" ? {} : undefined;
  return {
    tooltip: { trigger: "axis" },
    xAxis: { type: "category", data: xData },
    yAxis: { type: "value" },
    series: [{ type: seriesType, data: yData, areaStyle }]
  };
}

function render() {
  if (!el.value) return;
  if (!chart) chart = echarts.init(el.value);
  chart.setOption(buildOption(), true);
}

onMounted(() => {
  render();
  window.addEventListener("resize", onResize);
});

function onResize() {
  chart?.resize();
}

onBeforeUnmount(() => {
  window.removeEventListener("resize", onResize);
  chart?.dispose();
  chart = null;
});

watch(
  () => [props.type, props.rows, props.config],
  () => render(),
  { deep: true }
);
</script>

