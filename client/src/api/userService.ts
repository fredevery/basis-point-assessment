import api from './index'
import type { User } from './types'

type UserResponse = {
  user: User
  access: string
  error?: {
    code: string
    message: string
  }
}

export async function fetchCurrentUser(): Promise<UserResponse> {
  try {
    const response = await api().post('/auth/refresh/')
    return response.data as UserResponse
  } catch (error) {
    throw error
  }
}

export async function loginUser(code_name: string, password: string): Promise<UserResponse> {
  try {
    const response = await api().post('/auth/login/', { code_name, password })
    return response.data as UserResponse
  } catch (error) {
    throw error
  }
}
