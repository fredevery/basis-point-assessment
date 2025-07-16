import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'
import LoginView from '@/views/LoginView.vue'
import DashboardView from '@/views/DashboardView.vue'
import WelcomeView from '@/views/WelcomeView.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: WelcomeView,
    meta: { transition: 'vertical-slide' },
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: DashboardView,
    meta: { requiresAuth: true, transition: 'vertical-slide' },
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView,
    meta: { transition: 'vertical-slide' },
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

// Navigation guard for authentication

router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  if (to.meta.requiresAuth && !userStore.isAuthenticated) {
    next({ name: 'login' })
  } else if (to.name === 'login' && userStore.isAuthenticated) {
    next({ name: 'dashboard' })
  } else {
    next()
  }
})

export default router
