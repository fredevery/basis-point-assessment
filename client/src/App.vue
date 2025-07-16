<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
import { useUserStore } from '@/stores/user'
import SpinningGlobe from '@/components/SpinningGlobe.vue'

const userStore = useUserStore()
userStore.fetchCurrentUser()
</script>

<template>
  <div class="app-container">
    <main class="main-content">
      <RouterView v-if="!userStore.processing" v-slot="{ Component, route }">
        <Transition :name="(route.meta?.transition as string) || `fade`">
          <component :is="Component" :key="route.path" />
        </Transition>
      </RouterView>
      <div v-else class="loading">
        <p>Loading...</p>
      </div>
    </main>
  </div>
  <div class="crt-overlay"></div>
  <SpinningGlobe class="background-globe" v-if="userStore.isAuthenticated" />
  <div class="background">
    <Transition name="logo-transition">
      <img class="logo" src="/images/MI6_Logo.webp" v-if="!userStore.isAuthenticated" />
    </Transition>
  </div>

</template>

<style scoped>
.app-container {
  position: relative;
  z-index: 2;
  /* min-height: 100vh; */
}

.background-globe {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: -1;
  mix-blend-mode: multiply;
  /* Ensure it stays in the background */
}

.crt-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  mix-blend-mode: overlay;
  z-index: 1;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-image:
      radial-gradient(circle at 50% 50%, rgba(0, 0, 0, 0) 50%, rgb(50, 50, 50) 100%),
      url('@/assets/dither-noise.svg');
    filter: contrast(1.425) brightness(9) grayscale(100%);
    opacity: 0.35;
    z-index: 2;
  }

  &::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-image: repeating-linear-gradient(to bottom,
        rgba(0, 0, 0, 0.15) 0px,
        rgba(0, 0, 0, 0.15) 2px,
        transparent 2px,
        transparent 4px);
    pointer-events: none;
    z-index: 3;
  }
}

.background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
  pointer-events: none;

  .logo {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 30vw;
    height: auto;
    z-index: 10;
    mix-blend-mode: multiply;
    opacity: 0.25;

    &.logo-transition-enter-active,
    &.logo-transition-leave-active {
      transition: transform 0.3s ease-in-out, opacity 0.3s ease-in-out;
    }

    &.logo-transition-enter-from,
    &.logo-transition-leave-to {
      transform: translate(-50%, -50%) scale(0.5);
      opacity: 0;
    }

    &.logo-transition-enter-to,
    &.logo-transition-leave-from {
      transform: translate(-50%, -50%) scale(1);
      opacity: 0.25;
    }
  }

}
</style>
