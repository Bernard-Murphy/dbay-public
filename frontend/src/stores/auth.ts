import { defineStore } from "pinia";
import { ref, computed } from "vue";

export const useAuthStore = defineStore("auth", () => {
  const user = ref<any>({ id: "test-user-id", username: "testuser" }); // Default mock user
  const token = ref(localStorage.getItem("token") || "mock-token");

  const isAuthenticated = computed(() => !!token.value);

  function login(payload: any) {
    user.value = { ...payload.user, id: "test-user-id" };
    token.value = "mock-jwt-token";
    localStorage.setItem("token", token.value);
  }

  function logout() {
    user.value = null;
    token.value = null;
    localStorage.removeItem("token");
  }

  return { user, token, isAuthenticated, login, logout };
});
