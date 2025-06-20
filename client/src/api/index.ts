const BASE_API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000/api'

export const api = () => {
  console.log(`API Base URL: ${BASE_API_URL}`)
  return {
    get: (url: string, params?: Record<string, any>) => {
      console.log(`GET request to: ${BASE_API_URL + url}`, params)
      return fetch(BASE_API_URL + url + new URLSearchParams(params || {}), {
        method: 'GET',
      }).then((response) => response.json())
    },
    post: (url: string, body: Record<string, any>) => {
      return fetch(BASE_API_URL + url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(body),
      }).then((response) => response.json())
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
