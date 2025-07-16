const BASE_API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000/api'

export const api = () => {
  return {
    get: (url: string, params?: Record<string, any>) => {
      return fetch(BASE_API_URL + url + new URLSearchParams(params || {}), {
        credentials: 'include',
        method: 'GET',
      }).then((response) => response.json())
    },
    post: async (url: string, body: Record<string, any> = {}) => {
      const response = await fetch(BASE_API_URL + url, {
        mode: 'cors',
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(body),
      })
      const data = await response.json()
      return { data }
    },
    put: (url: string, body: Record<string, any>) => {
      return fetch(BASE_API_URL + url, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
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
