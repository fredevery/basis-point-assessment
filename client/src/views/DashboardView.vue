<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { storeToRefs } from 'pinia'
import { usePingStore, type Ping } from '@/stores/ping'
import { useUserStore } from '@/stores/user'

// Reference: See SPEC.md - "Ping Management: Fetching and Displaying Pings"
const pingStore = usePingStore()
const { pings, pingChains, processing, error, activePing, activePingChains } = storeToRefs(pingStore)
const userStore = useUserStore()
const { currentUser } = storeToRefs(userStore)
const showDashboard = ref(false)

onMounted(() => {
  pingStore.fetchAllPings()
})

function togglePingChain(event: Event) {
  const checkbox = event.target as HTMLInputElement
  const pingId = parseInt(checkbox.value, 10)

  const isActive = pingStore.toggleChain(pingId)
  if (isActive) {
    const lastPing = pingStore.getPingChain(pingId)[0];
    setActivePing(lastPing);
  } else {
    pingStore.setActivePing(null)
  }
}

function isActivePingChain(pingId: number): boolean {
  return pingStore.isInActiveChain(pingId)
}

function hasChildren(ping: Ping): boolean {
  return pings.value.find(p => p.parent_ping === ping.id) !== undefined
}

function setActivePing(ping: Ping) {
  pingStore.activateChain(ping.id);
  pingStore.setActivePing(ping)
}

function gotoPing(direction: number) {
  const activePing = pingStore.activePing
  if (!activePing) return
  const pingChain = pingStore.getPingChain(activePing.id)
  const currentIndex = pingChain.findIndex(p => p.id === activePing.id)
  const nextIndex = (currentIndex + direction + pingChain.length) % pingChain.length
  const nextPing = pingChain[nextIndex]
  setActivePing(nextPing)
}

function gotoLastPingInChain() {
  const activePing = pingStore.activePing
  if (!activePing) return
  const pingChain = pingStore.getPingChain(activePing.id)
  if (pingChain.length === 0) return
  const lastPing = pingChain[0]
  setActivePing(lastPing)
}

function filterPingChainsForDisplay(pingChains: Ping[][]): Ping[][] {
  return pingChains.filter(chain => {
    if (!activePingChains.value.length) return true; // Show all chains if no active ping
    return pingStore.isActivePingChain(chain);
  })
}
</script>

<template>
  <div class="dashboard-view">
    <Transition name="v">
      <div class="window active-agent-window" :class="{ 'minimized': showDashboard }" v-if="currentUser">
        <div class="window-header" v-if="currentUser && !showDashboard">
          <h3 class="window-title">Welcome Agent {{ currentUser.code_name }}</h3>
        </div>
        <div class="window-content">
          <div v-if="!currentUser">Loading active agent...</div>
          <div v-else-if="showDashboard">
            <p><strong>Active Agent:</strong> {{ currentUser.code_name }}</p>
          </div>
          <div v-else>
            <p>
              Welcome to the Top Secret Ping Mainframe. As an agent, your mission is to monitor, respond, and track pings with precision. Stay
              alert, and remember: every ping counts.
            </p>
            <div class="controls">
              <button class="button is-secondary button-small" @click="showDashboard = !showDashboard">Proceed</button>
            </div>
          </div>
        </div>
      </div>
    </Transition>
    <Transition name="v">
      <div class="window active-ping-window" v-if="activePing">
        <div class="window-header">
          <button class="button is-secondary button-small" @click="gotoPing(1)">&#9665;</button>
          <h3 class="window-title">Active Ping</h3>
          <button class="button is-secondary button-small" @click="gotoPing(-1)">&#9655;</button>
        </div>
        <div class="window-content">
          <div v-if="!activePing">No active ping selected.</div>
          <div v-else>
            <p><strong>Agent:</strong> {{ activePing.user.code_name }}</p>
            <p><strong>Ping ID:</strong> {{ activePing.id }}</p>
            <p><strong>Latitude:</strong> {{ activePing.latitude }}</p>
            <p><strong>Longitude:</strong> {{ activePing.longitude }}</p>
            <p><strong>Timestamp:</strong> {{ new Date(activePing.timestamp).toLocaleString() }}</p>
          </div>
        </div>
        <div class="controls">
          <button @click="pingStore.setActivePing(null)" class="button is-secondary button-small">Close</button>
          <button v-if="!hasChildren(activePing)" @click="pingStore.respondToPing(activePing.id)"
            class="button is-primary button-small">Respond</button>
          <button v-else @click="gotoLastPingInChain" class="button is-primary button-small">Last Ping</button>
        </div>
      </div>
    </Transition>
    <Transition name="v">

      <div class="window ping-window" v-if="showDashboard">
        <div class="window-header">
          <h3 class="window-title">Pings</h3>
        </div>
        <div class="window-content">
          <div v-if="processing">Loading pings...</div>
          <div v-else-if="error">{{ error }}</div>
          <div v-else>
            <div v-if="pings.length === 0">No pings found.</div>
            <table class="ping-table" v-else>
              <thead>
                <tr>
                  <th></th>
                  <th>Agent</th>
                  <th>Ping Count</th>
                  <th>Latitude</th>
                  <th>Longitude</th>
                  <th>Timestamp</th>
                  <th width="10%"></th>
                </tr>
              </thead>
              <TransitionGroup name="ping-row" tag="tbody">
                <template v-for="(pings) in filterPingChainsForDisplay(pingChains)">
                  <template v-for="(ping, index) in pings" :key="ping.id">
                    <tr v-if="index === 0 || isActivePingChain(ping.id)" :class="{ 'last-ping': index === 0 }" class="ping-row" :key="ping.id">
                      <td valign="middle">
                        <label class="checkbox" v-if="index === 0">
                          <input type="checkbox" @change="togglePingChain" :value="ping.id" :checked="isActivePingChain(ping.id)" />
                          <span class="checkmark"></span>
                        </label>
                        <template v-else>
                          <div v-if="index < pings.length - 1" class="ping-connector">&#9500;</div>
                          <div v-else class="ping-connector">&#9492;</div>
                        </template>
                      </td>
                      <td>{{ ping.user.code_name }}</td>
                      <td>{{ index === 0 ? pings.length : "" }}</td>
                      <td>{{ ping.latitude }}</td>
                      <td>{{ ping.longitude }}</td>
                      <td>{{ new Date(ping.timestamp).toLocaleString() }}</td>
                      <td width="10%"><button @click="setActivePing(ping)" class="button button-xsmall">Focus</button></td>
                    </tr>
                  </template>
                </template>
              </TransitionGroup>
            </table>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.dashboard-view {
  .active-agent-window {
    transition: transform 300ms;

    &.minimized {
      transform: translate(0, 0);
      font-size: 0.75rem;
      top: 1rem;
      left: 1rem;
      width: 10rem;

      .window-content {
        padding: 0.75rem;

        p {
          padding: 0;
          margin: 0;
          line-height: 1;
        }
      }
    }

    .window-header {
      justify-content: center;
    }

    .window-title {
      font-size: 1.5rem;
    }

    .controls {
      padding-top: 0.5rem;
      text-align: center;
    }
  }

  .active-ping-window {
    width: 20vw;
    font-size: 0.8rem;
    transform: translate(0, 0);
    top: initial;
    bottom: calc(50vh + 1rem);
    left: calc(50vw + 1rem);

    .window-header {
      padding: 0.5rem;
    }

    .window-content {
      padding: 0.5;
    }

    .controls {
      display: flex;
      justify-content: space-between;
      padding: 0.75rem;
      border-top: 1px solid var(--primary-color);
      gap: 0.5rem;

      .button.is-primary {
        flex: 1;
      }
    }
  }

  .ping-window {
    width: calc(100vw - 40px);
    top: initial;
    bottom: 1rem;
    left: 1rem;
    transform: translate(0, 0);

    .window-header {
      padding: 0.5rem;
    }

    .window-content {
      padding: 0;
    }
  }

  .active-agent-window,
  .active-ping-window,
  .ping-window {

    &.v-leave-from,
    &.v-enter-to {
      transform: translate(0, 0) scale(1);
      opacity: 1;
    }

    &.v-enter-active {
      transition-delay: 100ms;
    }

    &.v-enter-from,
    &.v-leave-to {
      transform: translate(0, 0) scale(0.75);
      opacity: 0;
    }
  }

  .ping-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.8rem;

    tbody {
      display: block;
      max-height: 25vh;
      overflow-y: auto;
      overflow-x: hidden;
      scrollbar-width: thin;
      scrollbar-color: var(--primary-color) transparent;

      &::-webkit-scrollbar {
        width: 8px;
        background: transparent;
      }

      &::-webkit-scrollbar-thumb {
        background: var(--primary-color);
        border-radius: 4px;
      }

      &::-webkit-scrollbar-track {
        background: transparent;
      }
    }

    th,
    td {
      text-align: left;
      padding: 0.25rem 0.5rem;
    }

    thead>tr {
      background-color: var(--secondary-color);
      border-left-color: transparent;
      display: table;
      table-layout: fixed;
      width: 100%;

      th:first-child {
        width: 2rem;
      }
    }

    .ping-row {
      display: table;
      table-layout: fixed;
      width: 100%;
      /* border: 1px solid transparent; */


      td {
        transition: padding-block 0.2s ease;
        padding: 0.1rem 0.5rem;

        &:first-child {
          width: 2rem;
          text-align: center;
          padding-block: 0;
          position: relative;
          overflow: hidden
        }
      }

      .ping-connector {
        font-size: 1.5rem;
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
      }

      &.hidden {
        display: none;
      }

      &.last-ping {
        border-top: 1px solid var(--primary-color);

        td {
          padding: 0.25rem 0.5rem;
        }

        td:first-child {
          padding-left: 0.5rem;
        }
      }

      &:nth-child(even) {
        background-color: var(--secondary-color);
      }

      &.ping-row-enter-active,
      &.ping-row-leave-active {
        transition: transform 300ms, opacity 300ms, max-height 300ms;
      }

      &.ping-row-leave-active {
        position: absolute;
      }

      &.ping-row-enter-from,
      &.ping-row-leave-to {
        transform: translateX(2rem);
        opacity: 0;
        max-height: 0;
      }

      &.ping-row-enter-to,
      &.ping-row-leave-from {
        transform: translateX(0%);
        opacity: 1;
        max-height: 3rem;
      }
    }
  }

  .checkbox {
    position: relative;
    display: inline-block;
    width: 1.2rem;
    height: 1.2rem;
    margin: 0;
    vertical-align: middle;
    cursor: pointer;
  }

  .checkbox input[type="checkbox"] {
    opacity: 0;
    width: 1.2rem;
    height: 1.2rem;
    margin: 0;
    position: absolute;
    left: 0;
    top: 0;
    cursor: pointer;
  }

  .checkbox .checkmark {
    position: absolute;
    left: 0;
    top: 0;
    width: 1.2rem;
    height: 1.2rem;
    background: var(--secondary-color);
    border: 1px solid var(--primary-color);
    border-radius: 0.3rem;
    transition: background 0.2s, border-color 0.2s;
  }

  .checkbox input[type="checkbox"]:checked+.checkmark {
    background: var(--primary-color);
    border-color: var(--secondary-color);
  }

  .checkbox .checkmark:after {
    content: "";
    position: absolute;
    display: none;
  }

  .checkbox input[type="checkbox"]:checked+.checkmark:after {
    display: block;
  }

  .checkbox .checkmark:after {
    left: 0.35rem;
    top: 0.15rem;
    width: 0.3rem;
    height: 0.6rem;
    border: solid var(--secondary-color);
    border-width: 0 0.2rem 0.2rem 0;
    transform: rotate(45deg);
    content: "";
  }
}
</style>
