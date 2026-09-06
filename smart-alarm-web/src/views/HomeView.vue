<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const API_URL = import.meta.env.VITE_API_URL

const alarms = ref([])
const alarmStatus = ref('')
const errorMessage = ref('')
const isLoading = ref(true)

let pollingInterval

async function loadAlarms() {
  const token = localStorage.getItem('token')

  if (!token) {
    router.push('/login')
    return
  }

  try {
    const response = await fetch(`${API_URL}/alarms`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })

    if (response.status === 401) {
      localStorage.removeItem('token')
      router.push('/login')
      return
    }

    if (!response.ok) {
      errorMessage.value = 'Failed to load alarm history'
      return
    }

    alarms.value = await response.json()
  } catch (error) {
    errorMessage.value = 'Server connection failed'
  }
}

async function loadStatus() {
  try {
    const response = await fetch(`${API_URL}/status`)

    if (!response.ok) {
      errorMessage.value = 'Failed to load alarm status'
      return
    }

    const data = await response.json()
    alarmStatus.value = data.status
  } catch (error) {
    errorMessage.value = 'Server connection failed'
  }
}

async function changeAlarmStatus(action) {
  try {
    const response = await fetch(`${API_URL}/${action}`, {
      method: 'POST',
    })

    if (!response.ok) {
      errorMessage.value = 'Failed to change alarm status'
      return
    }

    await loadStatus()
  } catch (error) {
    errorMessage.value = 'Server connection failed'
  }
}

function logout() {
  localStorage.removeItem('token')
  router.push('/login')
}

onMounted(async () => {
  await Promise.all([loadAlarms(), loadStatus()])

  pollingInterval = setInterval(async () => {
    await Promise.all([loadAlarms(), loadStatus()])
  }, 2000)

  isLoading.value = false
})

onUnmounted(() => {
  clearInterval(pollingInterval)
})
</script>

<template>
  <main class="dashboard">
    <header class="dashboard-header">
      <div>
        <p class="eyebrow">Raspberry Pi Security System</p>
        <h1>Smart Alarm Dashboard</h1>
      </div>

      <button class="logout-button" @click="logout">Logout</button>
    </header>

    <p v-if="isLoading" class="message">Loading...</p>

    <p v-if="errorMessage" class="error-message">
      {{ errorMessage }}
    </p>

    <div v-if="!isLoading && !errorMessage">
      <section class="overview-grid">
        <article class="card status-card">
          <div class="card-header">
            <div>
              <p class="card-label">System status</p>
              <h2>Alarm</h2>
            </div>

            <span
              class="status-badge"
              :class="{
                active: alarmStatus === 'ON',
                inactive: alarmStatus === 'OFF',
              }"
            >
              {{ alarmStatus }}
            </span>
          </div>

          <p class="status-description">
            {{
              alarmStatus === 'ON'
                ? 'The system is active and Raspberry Pi can send motion alarms.'
                : 'The system is inactive. Motion alarms are currently blocked.'
            }}
          </p>

          <div class="actions">
            <button
              class="action-button activate-button"
              @click="changeAlarmStatus('activate')"
              :disabled="alarmStatus === 'ON'"
            >
              Activate
            </button>

            <button
              class="action-button deactivate-button"
              @click="changeAlarmStatus('deactivate')"
              :disabled="alarmStatus === 'OFF'"
            >
              Deactivate
            </button>
          </div>
        </article>

        <article class="card summary-card">
          <p class="card-label">Alarm history</p>

          <div class="summary-value">
            {{ alarms.length }}
          </div>

          <p class="summary-description">Total stored motion events</p>
        </article>

        <article class="card summary-card">
          <p class="card-label">Connection</p>

          <div class="connection-status">
            <span class="connection-dot"></span>
            Online
          </div>

          <p class="summary-description">FastAPI server is responding</p>
        </article>
      </section>

      <section class="card history-card">
        <div class="history-header">
          <div>
            <p class="card-label">Events</p>
            <h2>Alarm History</h2>
          </div>

          <span class="history-count"> {{ alarms.length }} events </span>
        </div>

        <div class="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Type</th>
                <th>Date and time</th>
              </tr>
            </thead>

            <tbody>
              <tr v-for="alarm in alarms" :key="alarm.id">
                <td>#{{ alarm.id }}</td>

                <td>
                  <span class="event-type">
                    {{ alarm.type }}
                  </span>
                </td>

                <td>
                  {{ new Date(alarm.created_at).toLocaleString() }}
                </td>
              </tr>

              <tr v-if="alarms.length === 0">
                <td colspan="3" class="empty-state">No alarm events yet.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </div>
  </main>
</template>

<style scoped>
.dashboard {
  min-height: 100vh;
  padding: 40px;
  background: #f5f7fb;
  color: #1f2937;
  font-family:
    Inter,
    system-ui,
    -apple-system,
    BlinkMacSystemFont,
    'Segoe UI',
    sans-serif;
}

.dashboard-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  margin-bottom: 32px;
}

.dashboard-header h1 {
  margin: 4px 0 0;
  font-size: 32px;
  line-height: 1.2;
}

.eyebrow,
.card-label {
  margin: 0;
  color: #6b7280;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.logout-button {
  padding: 10px 18px;
  border: 1px solid #d1d5db;
  border-radius: 10px;
  background: white;
  color: #374151;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
}

.logout-button:hover {
  background: #f9fafb;
}

.overview-grid {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr;
  gap: 20px;
  margin-bottom: 24px;
}

.card {
  border: 1px solid #e5e7eb;
  border-radius: 18px;
  background: white;
  box-shadow: 0 8px 30px rgba(15, 23, 42, 0.05);
}

.status-card,
.summary-card {
  padding: 24px;
}

.card-header,
.history-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 20px;
}

.card-header h2,
.history-header h2 {
  margin: 5px 0 0;
  font-size: 22px;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 64px;
  padding: 7px 12px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 800;
}

.status-badge.active {
  background: #dcfce7;
  color: #166534;
}

.status-badge.inactive {
  background: #fee2e2;
  color: #991b1b;
}

.status-description {
  max-width: 620px;
  margin: 20px 0 24px;
  color: #6b7280;
  line-height: 1.6;
}

.actions {
  display: flex;
  gap: 12px;
}

.action-button {
  padding: 11px 20px;
  border: 0;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
}

.activate-button {
  background: #111827;
  color: white;
}

.deactivate-button {
  background: #ef4444;
  color: white;
}

.action-button:disabled {
  cursor: not-allowed;
  opacity: 0.4;
}

.summary-value {
  margin-top: 18px;
  font-size: 42px;
  font-weight: 800;
}

.summary-description {
  margin: 8px 0 0;
  color: #6b7280;
  font-size: 14px;
  line-height: 1.5;
}

.connection-status {
  display: flex;
  align-items: center;
  gap: 9px;
  margin-top: 24px;
  font-size: 20px;
  font-weight: 700;
}

.connection-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #22c55e;
  box-shadow: 0 0 0 5px #dcfce7;
}

.history-card {
  overflow: hidden;
}

.history-header {
  padding: 24px;
  border-bottom: 1px solid #e5e7eb;
}

.history-count {
  padding: 6px 10px;
  border-radius: 999px;
  background: #f3f4f6;
  color: #4b5563;
  font-size: 13px;
  font-weight: 700;
}

.table-wrapper {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th,
td {
  padding: 16px 24px;
  text-align: left;
}

th {
  background: #f9fafb;
  color: #6b7280;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

td {
  border-top: 1px solid #f3f4f6;
  color: #374151;
  font-size: 14px;
}

tbody tr:hover {
  background: #fafafa;
}

.event-type {
  display: inline-block;
  padding: 5px 9px;
  border-radius: 999px;
  background: #fff7ed;
  color: #c2410c;
  font-size: 12px;
  font-weight: 800;
}

.message,
.error-message {
  padding: 16px;
  border-radius: 12px;
  background: white;
}

.error-message {
  border: 1px solid #fecaca;
  background: #fef2f2;
  color: #b91c1c;
}

.empty-state {
  padding: 40px;
  text-align: center;
  color: #9ca3af;
}

@media (max-width: 900px) {
  .dashboard {
    padding: 24px;
  }

  .overview-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 600px) {
  .dashboard {
    padding: 18px;
  }

  .dashboard-header {
    align-items: flex-start;
    flex-direction: column;
  }

  .dashboard-header h1 {
    font-size: 26px;
  }

  .actions {
    flex-direction: column;
  }

  .action-button {
    width: 100%;
  }

  th,
  td {
    padding: 14px 16px;
  }
}
</style>
