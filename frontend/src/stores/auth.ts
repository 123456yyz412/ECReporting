import { defineStore } from "pinia";
import { http } from "../api/http";

type Me = {
  id: number;
  username: string;
  is_admin: boolean;
  groups: string[];
};

export const useAuthStore = defineStore("auth", {
  state: () => ({
    accessToken: localStorage.getItem("accessToken") || "",
    refreshToken: localStorage.getItem("refreshToken") || "",
    me: null as Me | null,
    meLoaded: false
  }),
  actions: {
    async login(username: string, password: string) {
      const { data } = await http.post("/api/auth/token/", { username, password });
      this.accessToken = data.access;
      this.refreshToken = data.refresh;
      localStorage.setItem("accessToken", this.accessToken);
      localStorage.setItem("refreshToken", this.refreshToken);
      await this.fetchMe();
    },
    logout() {
      this.accessToken = "";
      this.refreshToken = "";
      this.me = null;
      this.meLoaded = false;
      localStorage.removeItem("accessToken");
      localStorage.removeItem("refreshToken");
    },
    async refresh() {
      const { data } = await http.post("/api/auth/refresh/", { refresh: this.refreshToken });
      this.accessToken = data.access;
      localStorage.setItem("accessToken", this.accessToken);
    },
    async fetchMe() {
      const { data } = await http.get("/api/me/");
      this.me = data;
      this.meLoaded = true;
    }
  }
});

