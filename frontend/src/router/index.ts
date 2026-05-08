import { createRouter, createWebHistory, type RouteRecordRaw } from "vue-router";
import { useAuthStore } from "../stores/auth";

import LoginView from "../views/LoginView.vue";
import MainLayout from "../layouts/MainLayout.vue";
import HomeView from "../views/HomeView.vue";
import CollectionsView from "../views/reports/CollectionsView.vue";
import CollectionDetailView from "../views/reports/CollectionDetailView.vue";
import QueryEditorView from "../views/reports/QueryEditorView.vue";
import DashboardEditorView from "../views/reports/DashboardEditorView.vue";
import UploadModulesView from "../views/datafill/UploadModulesView.vue";
import AdminHomeView from "../views/admin/AdminHomeView.vue";
import DataSourcesView from "../views/admin/DataSourcesView.vue";
import UsersView from "../views/admin/UsersView.vue";
import GroupsView from "../views/admin/GroupsView.vue";
import BrandingView from "../views/admin/BrandingView.vue";

const routes: RouteRecordRaw[] = [
  { path: "/login", component: LoginView },
  {
    path: "/",
    component: MainLayout,
    children: [
      { path: "", component: HomeView },
      { path: "reports", component: CollectionsView },
      { path: "reports/collections/:id", component: CollectionDetailView, props: true },
      { path: "reports/queries/:id", component: QueryEditorView, props: true },
      { path: "reports/dashboards/:id", component: DashboardEditorView, props: true },
      { path: "datafill", component: UploadModulesView },
      { path: "admin", component: AdminHomeView },
      { path: "admin/datasources", component: DataSourcesView },
      { path: "admin/users", component: UsersView },
      { path: "admin/groups", component: GroupsView },
      { path: "admin/branding", component: BrandingView }
    ]
  }
];

export const router = createRouter({
  history: createWebHistory(),
  routes
});

router.beforeEach(async (to) => {
  const auth = useAuthStore();
  if (to.path === "/login") return true;
  if (!auth.accessToken) {
    return "/login";
  }
  if (!auth.meLoaded) {
    try {
      await auth.fetchMe();
    } catch {
      auth.logout();
      return "/login";
    }
  }
  return true;
});
