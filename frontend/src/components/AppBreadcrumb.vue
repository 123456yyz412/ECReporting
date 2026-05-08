<template>
  <div class="breadcrumb-wrap">
    <el-breadcrumb separator=">">
      <el-breadcrumb-item v-for="(item, idx) in items" :key="`${idx}-${item.label}`">
        <a v-if="item.to" class="crumb-link" @click.prevent="go(item.to)">{{ item.label }}</a>
        <span v-else class="crumb-current">{{ item.label }}</span>
      </el-breadcrumb-item>
    </el-breadcrumb>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from "vue-router";

type BreadcrumbItem = {
  label: string;
  to?: string;
};

defineProps<{
  items: BreadcrumbItem[];
}>();

const router = useRouter();

function go(to: string) {
  router.push(to);
}
</script>

<style scoped>
.breadcrumb-wrap {
  margin-bottom: 10px;
}

.crumb-link {
  color: var(--text-secondary, #475569);
  text-decoration: none;
  cursor: pointer;
}

.crumb-link:hover {
  color: var(--text-primary, #0f172a);
}

.crumb-current {
  color: var(--text-primary, #0f172a);
  font-weight: 600;
}
</style>
