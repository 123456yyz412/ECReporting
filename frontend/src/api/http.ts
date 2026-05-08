import axios from "axios";
import { useAuthStore } from "../stores/auth";

export const http = axios.create({
  baseURL: "",
  timeout: 30000
});

http.interceptors.request.use((config) => {
  const auth = useAuthStore();
  if (auth.accessToken) {
    config.headers = config.headers ?? {};
    config.headers.Authorization = `Bearer ${auth.accessToken}`;
  }
  return config;
});

let refreshing: Promise<void> | null = null;

http.interceptors.response.use(
  (r) => r,
  async (err) => {
    const auth = useAuthStore();
    const status = err?.response?.status;
    const original = err?.config;
    if (status !== 401 || !auth.refreshToken || original?._retry) {
      throw err;
    }
    original._retry = true;
    if (!refreshing) {
      refreshing = auth
        .refresh()
        .catch(() => {
          auth.logout();
          throw err;
        })
        .finally(() => {
          refreshing = null;
        });
    }
    await refreshing;
    return http(original);
  }
);

