import api from './index'
import type { User } from './types'

export async function fetchCurrentUser(): Promise<User> {
  try {
    const response = await api().get('/test_user')
    return response as User
  } catch (error) {
    console.error('Error fetching current user:', error)
    throw error
  }
}
