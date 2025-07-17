<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { storeToRefs } from 'pinia'
import { usePingStore, type Ping } from '@/stores/ping'

// Reference: See SPEC.md - "Ping Management: Fetching and Displaying Pings"
const pingStore = usePingStore()
const { pings, pingChains, processing, error, activePing } = storeToRefs(pingStore)

onMounted(() => {
  pingStore.fetchAllPings()
})

function togglePingChain(event: Event) {
  const checkbox = event.target as HTMLInputElement
  const pingId = parseInt(checkbox.value, 10)

  pingStore.toggleChain(pingId)
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
</script>

<template>
  <div class="dashboard-view">
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

      <div class="window ping-window" v-if="!activePing">
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
              <tbody>
                <template v-for="(pings) in pingChains">
                  <tr v-for="(ping, index) in pings" :key="ping.id"
                    :class="{ 'last-ping': index === 0, 'hidden': index > 0 && !isActivePingChain(ping.id) }" class="ping-row">
                    <td valign="middle">
                      <label class="checkbox" v-if="index === 0">
                        <input type="checkbox" @change="togglePingChain" :value="ping.id" :checked="isActivePingChain(ping.id)" />
                        <span class="checkmark"></span>
                      </label>
                    </td>
                    <td>{{ ping.user.code_name }}</td>
                    <td>{{ index === 0 ? pings.length : "" }}</td>
                    <td>{{ ping.latitude }}</td>
                    <td>{{ ping.longitude }}</td>
                    <td>{{ new Date(ping.timestamp).toLocaleString() }}</td>
                    <td width="10%"><button @click="setActivePing(ping)" class="button button-xsmall">Focus</button></td>
                  </tr>
                </template>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.dashboard-view {

  .active-ping-window {
    width: 20vw;
    font-size: 0.8rem;
    transform: translate(0, 0);
    top: initial;
    bottom: calc(50vh + 20px);
    left: calc(50vw + 20px);

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

  .ping-window {
    width: calc(100vw - 40px);
    top: initial;
    bottom: 20px;
    left: 20px;
    transform: translate(0, 0);

    .window-header {
      padding: 0.5rem;
    }

    .window-content {
      padding: 0;
    }

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
      border: 1px solid transparent;


      td {
        transition: padding-block 0.2s ease;
        padding: 0.1rem 0.5rem;

        &:first-child {
          padding-left: 2rem;
          width: 2rem;
        }
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

      &:hover {
        border: 1px solid var(--primary-color);
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
