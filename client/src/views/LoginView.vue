<script lang="ts" setup>
import { ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores/user'

const userStore = useUserStore();
const router = useRouter();

watch(() => userStore.isAuthenticated, (isAuthenticated) => {
  if (isAuthenticated) {
    router.push({ name: 'dashboard' });
  }
}, { immediate: true });

const username = ref('');
const password = ref('');
const loading = ref(false);
const error = ref({
  code: '',
  message: ''
});

const onSubmit = async (event: Event) => {
  loading.value = true;
  try {
    const response = await userStore.login(username.value, password.value);
    console.log('Login response:', response);
    if (response?.error) {
      error.value = response.error;
      return;
    }
  } finally {
    loading.value = false;
  }

}
</script>

<template>
  <section class="login-window window">
    <div class="window-header">
      <h3 class="window-title">Login</h3>
    </div>
    <div class="window-content">
      <form @submit.prevent="onSubmit">
        <div class="form-error" v-if="error.code">
          <p class="error-message">{{ error.message }}</p>
        </div>
        <div class="field">
          <label class="label" for="username">Agent Code:</label>
          <input v-model="username" id="username" class="input" type="text" placeholder="00X" />
        </div>
        <div class="field">
          <label class="label" for="password">Password:</label>
          <input v-model="password" id="password" class="input" type="password" placeholder="••••••••" />
        </div>
        <div class="controls">
          <button class="button is-primary" type="submit">Login</button>
        </div>
      </form>
    </div>
  </section>
</template>

<style scoped>
.login-window {
  width: 30rem;
  max-width: 95vw;
}
</style>
