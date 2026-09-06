<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const API_URL = import.meta.env.VITE_API_URL

const username = ref('')
const password = ref('')
const errorMessage = ref('')
const isLoggingIn = ref(false)

async function login() {
  errorMessage.value = ''
  isLoggingIn.value = true

  try {
    const response = await fetch(`${API_URL}/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username: username.value,
        password: password.value,
      }),
    })

    if (!response.ok) {
      errorMessage.value = 'Invalid username or password'
      return
    }

    const data = await response.json()

    localStorage.setItem('token', data.access_token)

    router.push('/')
  } catch (error) {
    errorMessage.value = 'Server connection failed'
  } finally {
    isLoggingIn.value = false
  }
}
</script>

<template>
  <main class="login-page">
    <section class="login-card">
      <div class="alarm-icon">
        <span>●</span>
      </div>

      <div class="login-heading">
        <p class="eyebrow">Raspberry Pi Security System</p>
        <h1>Smart Alarm</h1>
        <p class="subtitle">Sign in to access your alarm dashboard</p>
      </div>

      <form class="login-form" @submit.prevent="login">
        <div class="form-field">
          <label for="username">Username</label>

          <input
            id="username"
            v-model="username"
            type="text"
            placeholder="Enter your username"
            autocomplete="username"
            required
          />
        </div>

        <div class="form-field">
          <label for="password">Password</label>

          <input
            id="password"
            v-model="password"
            type="password"
            placeholder="Enter your password"
            autocomplete="current-password"
            required
          />
        </div>

        <p v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </p>

        <button class="login-button" type="submit" :disabled="isLoggingIn">
          {{ isLoggingIn ? 'Signing in...' : 'Sign in' }}
        </button>
      </form>

      <div class="system-status">
        <span class="status-dot"></span>
        Smart Alarm System
      </div>
    </section>
  </main>
</template>

<style scoped>
.login-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 24px;
  background:
    radial-gradient(circle at top left, rgba(59, 130, 246, 0.08), transparent 35%), #f5f7fb;
  color: #1f2937;
  font-family:
    Inter,
    system-ui,
    -apple-system,
    BlinkMacSystemFont,
    'Segoe UI',
    sans-serif;
}

.login-card {
  width: 100%;
  max-width: 420px;
  padding: 40px;
  border: 1px solid #e5e7eb;
  border-radius: 20px;
  background: white;
  box-shadow: 0 20px 50px rgba(15, 23, 42, 0.08);
}

.alarm-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 52px;
  height: 52px;
  margin-bottom: 24px;
  border-radius: 14px;
  background: #111827;
}

.alarm-icon span {
  position: relative;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #ef4444;
  color: transparent;
}

.alarm-icon span::after {
  position: absolute;
  top: -6px;
  left: -6px;
  width: 24px;
  height: 24px;
  border: 1px solid rgba(239, 68, 68, 0.4);
  border-radius: 50%;
  content: '';
}

.login-heading {
  margin-bottom: 30px;
}

.eyebrow {
  margin: 0 0 6px;
  color: #6b7280;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.login-heading h1 {
  margin: 0;
  color: #111827;
  font-size: 30px;
  line-height: 1.2;
}

.subtitle {
  margin: 10px 0 0;
  color: #6b7280;
  font-size: 14px;
  line-height: 1.5;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-field label {
  color: #374151;
  font-size: 13px;
  font-weight: 700;
}

.form-field input {
  width: 100%;
  box-sizing: border-box;
  padding: 13px 14px;
  border: 1px solid #d1d5db;
  border-radius: 10px;
  outline: none;
  background: #ffffff;
  color: #111827;
  font-size: 14px;
  transition:
    border-color 0.2s,
    box-shadow 0.2s;
}

.form-field input::placeholder {
  color: #9ca3af;
}

.form-field input:focus {
  border-color: #6b7280;
  box-shadow: 0 0 0 3px rgba(107, 114, 128, 0.1);
}

.login-button {
  width: 100%;
  margin-top: 4px;
  padding: 13px 20px;
  border: 0;
  border-radius: 10px;
  background: #111827;
  color: white;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  transition:
    transform 0.15s,
    background 0.15s;
}

.login-button:hover:not(:disabled) {
  background: #1f2937;
  transform: translateY(-1px);
}

.login-button:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.error-message {
  margin: 0;
  padding: 11px 13px;
  border: 1px solid #fecaca;
  border-radius: 9px;
  background: #fef2f2;
  color: #b91c1c;
  font-size: 13px;
}

.system-status {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 30px;
  padding-top: 22px;
  border-top: 1px solid #f3f4f6;
  color: #9ca3af;
  font-size: 12px;
}

.status-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #22c55e;
}

@media (max-width: 500px) {
  .login-page {
    padding: 16px;
  }

  .login-card {
    padding: 28px 24px;
  }
}
</style>
