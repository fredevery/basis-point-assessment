<script setup lang="ts"></script>

<template>
  <div class="welcome-window window">
    <div class="window-header">
      <h1>Welcome Agent</h1>
    </div>
    <div class="window-content">
      <p>
        Welcome to MI6, Agent. Your mission awaits. Please proceed with utmost discretion and professionalism.
      </p>
      <div class="controls">
        <router-link to="/login" class="login-link button">
          Proceed to Login
        </router-link>
      </div>
    </div>
  </div>
</template>

<style lang="css" scoped>
.welcome-window {
  .window-header {
    justify-content: center;
  }

  h1 {
    font-size: 1.5rem;
    text-align: center;
  }

  p {
    text-align: center;
    margin-bottom: 1rem;
  }

  .controls {
    display: flex;
    justify-content: center;
  }
}
</style>
