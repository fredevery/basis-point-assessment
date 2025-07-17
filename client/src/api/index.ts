import { useUserStore } from '@/stores/user'
const BASE_API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000/api'

export const api = () => {
  const getFetchHeaders = () => {
    const userStore = useUserStore()
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    }
    if (userStore.accessToken) {
      headers['Authorization'] = `Bearer ${userStore.accessToken}`
    }
    return headers
  }
  return {
    get: async (url: string, params?: Record<string, any>) => {
      const response = await fetch(BASE_API_URL + url + new URLSearchParams(params || {}), {
        headers: getFetchHeaders(),
        mode: 'cors',
        credentials: 'include',
        method: 'GET',
      })
      const data = await response.json()
      return { data }
    },
    post: async (url: string, body: Record<string, any> = {}) => {
      const response = await fetch(BASE_API_URL + url, {
        mode: 'cors',
        method: 'POST',
        headers: getFetchHeaders(),
        credentials: 'include',
        body: JSON.stringify(body),
      })
      const data = await response.json()
      return { data }
    },
    put: (url: string, body: Record<string, any>) => {
      return fetch(BASE_API_URL + url, {
        method: 'PUT',
        headers: getFetchHeaders(),
        body: JSON.stringify(body),
      }).then((response) => response.json())
    },
    delete: (url: string) => {
      return fetch(BASE_API_URL + url, {
        method: 'DELETE',
      }).then((response) => response.json())
    },
  }
}

export default api
