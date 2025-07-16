import { defineStore } from 'pinia'
import { fetchCurrentUser, loginUser } from '@/api/userService'
import type { User } from '@/api/types'

export const useUserStore = defineStore('user', {
  state: () => ({
    currentUser: null as User | null,
    accessToken: null as string | null,
    processing: false,
  }),
  getters: {
    isAuthenticated: (state) => state.currentUser && state.accessToken,
  },
  actions: {
    async fetchCurrentUser() {
      this.processing = true
      try {
        const fetchResponse = await fetchCurrentUser()
        this.setCurrentUser(fetchResponse.user)
        this.setAccessToken(fetchResponse.access)
      } catch (error) {
        this.unsetUser()
      }
      this.processing = false
    },
    async login(username: string, password: string) {
      try {
        const loginResponse = await loginUser(username, password)
        this.setCurrentUser(loginResponse.user)
        this.setAccessToken(loginResponse.access)
        return loginResponse
      } catch (error) {
        this.unsetUser()
      }
    },
    setCurrentUser(user: User | null) {
      this.currentUser = user
    },
    setAccessToken(token: string | null) {
      this.accessToken = token
    },
    unsetUser() {
      this.currentUser = null
      this.accessToken = null
    },
  },
})
