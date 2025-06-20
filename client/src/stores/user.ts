import { defineStore } from 'pinia'
import { fetchCurrentUser } from '@/api/userService'
import type { User } from '@/api/types'

export const useUserStore = defineStore('user', {
  state: () => ({
    currentUser: null as User | null,
  }),
  actions: {
    async loadCurrentUser() {
      try {
        this.currentUser = await fetchCurrentUser()
      } catch (error) {
        console.error('Failed to load current user:', error)
        this.currentUser = null
      }
    },
  },
  getters: {
    isAuthenticated: (state) => !!state.currentUser,
  },
})
