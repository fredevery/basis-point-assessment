// Ping Service for James Bond Ping Mission
// Implements endpoints as described in .project/BRIEF.md
import api from './index'
import type { User } from './types'

export type Ping = {
  id: number
  parent_ping: number | null
  latitude: number
  longitude: number
  timestamp: string
  user: User
}

export type PingResponse = {
  ping: Ping
  error?: {
    code: string
    message: string
  }
}

export type PingsResponse = {
  pings: Ping[]
  error?: {
    code: string
    message: string
  }
}

// Create a new ping (optionally as a response to the latest ping)
export async function createPing(parent?: number): Promise<PingResponse> {
  try {
    // Generate random coordinates for the ping
    const latitude = +(Math.random() * 180 - 90).toFixed(6)
    const longitude = +(Math.random() * 360 - 180).toFixed(6)
    const payload: any = { latitude, longitude }
    if (parent) payload.parent = parent
    const response = await api().post('/pings', payload)
    return response.data as PingResponse
  } catch (error) {
    throw error
  }
}

// Get all pings for the logged-in user
export async function fetchAllPings(): Promise<PingsResponse> {
  try {
    const response = await api().get('/pings')
    return { pings: response.data.results } as PingsResponse
  } catch (error) {
    throw error
  }
}

// Get the latest three pings for the logged-in user
export async function fetchLatestPings(): Promise<PingsResponse> {
  try {
    const response = await api().get('/pings/latest')
    return response.data as PingsResponse
  } catch (error) {
    throw error
  }
}

// Respond to a specific ping (trail creation)
export async function respondToPing(parentId: number): Promise<PingResponse> {
  try {
    // Generate random coordinates for the response ping
    const latitude = +(Math.random() * 180 - 90).toFixed(6)
    const longitude = +(Math.random() * 360 - 180).toFixed(6)
    const payload = { latitude, longitude }
    const response = await api().post(`/pings/${parentId}/respond/`, payload)
    return response.data as PingResponse
  } catch (error) {
    throw error
  }
}
