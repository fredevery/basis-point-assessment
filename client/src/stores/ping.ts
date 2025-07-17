import { defineStore } from 'pinia'
import { createPing, fetchAllPings, fetchLatestPings, respondToPing } from '@/api/pingService'
import type { Ping } from '@/api/pingService'
export type { Ping } from '@/api/pingService'

const getPingChain = (ping: Ping, pings: Ping[]): Ping[] => {
  const chain: Ping[] = [ping]
  let currentPing: Ping | null = ping

  while (currentPing?.parent_ping) {
    currentPing = pings.find((p) => p.id === currentPing?.parent_ping) || null
    if (currentPing) {
      chain.unshift(currentPing)
    } else {
      break
    }
  }

  return chain.reverse()
}

const pingIsInChain = (ping: Ping, chains: Ping[][]): boolean => {
  return chains.some((chain) => chain.some((p) => p.id === ping.id))
}

// Pinia store for managing pings, following the pattern in user.ts
export const usePingStore = defineStore('ping', {
  state: () => ({
    pings: [] as Ping[],
    latestPings: [] as Ping[],
    processing: false,
    error: null as string | null,
    activePing: null as Ping | null,
    activatedChains: [] as number[],
  }),
  getters: {
    pingChains(state) {
      const chains: Ping[][] = []
      state.pings.forEach((ping) => {
        if (pingIsInChain(ping, chains)) return
        const chain = getPingChain(ping, state.pings)
        chains.push(chain)
      })
      return chains
    },
    activePingChains(state) {
      const chains: Ping[][] = []
      state.activatedChains.forEach((pingId) => {
        chains.push(this.pingChains.find((c) => c.find((p) => p.id === pingId)) || [])
      })
      return chains
    },
  },
  actions: {
    async fetchAllPings() {
      this.processing = true
      try {
        const response = await fetchAllPings()
        this.pings = response.pings
        this.error = null
      } catch (error: any) {
        this.error = error?.message || 'Failed to fetch pings'
      }
      this.processing = false
    },
    async fetchLatestPings() {
      this.processing = true
      try {
        const response = await fetchLatestPings()
        this.latestPings = response.pings
        this.error = null
      } catch (error: any) {
        this.error = error?.message || 'Failed to fetch latest pings'
      }
      this.processing = false
    },
    async createPing(parent?: number) {
      this.processing = true
      try {
        const response = await createPing(parent)
        // Optionally, update pings or latestPings here
        this.error = null
        return response.ping
      } catch (error: any) {
        this.error = error?.message || 'Failed to create ping'
      }
      this.processing = false
    },
    async respondToPing(parentId: number) {
      this.processing = true
      let response: { ping: Ping } | null = null
      try {
        response = await respondToPing(parentId)
        this.error = null
      } catch (error: any) {
        this.error = error?.message || 'Failed to respond to ping'
      }
      this.processing = false

      if (response?.ping) {
        await this.fetchAllPings() // Refresh pings after responding
        this.setActivePing(response.ping)
      }
    },
    async setActivePing(ping: Ping | null) {
      this.activePing = ping ? this.pings.find((p) => p.id === ping?.id) || null : null
    },
    clearError() {
      this.error = null
    },
    activateChain(pingId: number) {
      if (!this.activatedChains.includes(pingId)) {
        this.activatedChains.push(pingId)
      }
    },
    deactivateChain(pingId: number) {
      this.activatedChains = this.activatedChains.filter((index) => index !== pingId)
    },
    toggleChain(pingId: number) {
      if (this.activatedChains.includes(pingId)) {
        this.deactivateChain(pingId)
      } else {
        this.activateChain(pingId)
      }
    },
    isInActiveChain(pingId: number): boolean {
      return this.activePingChains.find((c) => c.find((p) => p.id === pingId)) !== undefined
    },
    getPingChain(pingId: number): Ping[] {
      return this.pingChains.find((c) => c.find((p) => p.id === pingId)) || []
    },
  },
})
