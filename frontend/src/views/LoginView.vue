```vue
<template>
  <v-container fluid class="login-page pa-0">
    <v-row class="fill-height ma-0" align="center" justify="center">
      <v-col cols="12" sm="10" md="7" lg="4">

        <v-card class="login-card">
          <v-card-text class="pa-8">

            <div class="text-center mb-8">
              <div class="logo-wrapper mb-4">
                <v-icon size="70" color="white">
                  mdi-flask-outline
                </v-icon>
              </div>

              <h1 class="text-h4 font-weight-bold text-black mb-2">
                Chemical Docs
              </h1>

              <p class="text-black">
                Система управления реагентами и документацией
              </p>
            </div>

            <v-form
              ref="form"
              v-model="isFormValid"
              @submit.prevent="handleLogin"
            >
              <v-text-field
                v-model="username"
                label="Имя пользователя"
                prepend-inner-icon="mdi-account-outline"
                variant="outlined"
                density="comfortable"
                bg-color="white"
                :rules="[v => !!v || 'Введите имя пользователя']"
                class="mb-4"
              />

              <v-text-field
                v-model="password"
                label="Пароль"
                prepend-inner-icon="mdi-lock-outline"
                :append-inner-icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"
                @click:append-inner="showPassword = !showPassword"
                :type="showPassword ? 'text' : 'password'"
                variant="outlined"
                density="comfortable"
                bg-color="white"
                :rules="[v => !!v || 'Введите пароль']"
                class="mb-4"
              />

              <v-alert
                v-if="errorMessage"
                type="error"
                variant="tonal"
                class="mb-4"
                closable
                @click:close="errorMessage = ''"
              >
                {{ errorMessage }}
              </v-alert>

              <v-btn
                type="submit"
                block
                size="large"
                color="primary"
                :loading="loading"
                :disabled="!isFormValid"
                class="login-btn"
              >
                Войти в систему
              </v-btn>
            </v-form>

          </v-card-text>
        </v-card>

      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import api from '../utils/api'

export default {
  name: 'LoginView',

  data() {
    return {
      username: '',
      password: '',
      loading: false,
      isFormValid: false,
      errorMessage: '',
      showPassword: false
    }
  },

  methods: {
    async handleLogin() {
      if (!this.isFormValid) return

      this.loading = true
      this.errorMessage = ''

      try {
        const response = await api.post('/auth/login', {
          username: this.username,
          password: this.password
        })

        localStorage.setItem(
          'token',
          response.data.access_token
        )

        this.$router.push('/')
      } catch (error) {
        if (
          error.response &&
          error.response.status === 401
        ) {
          this.errorMessage =
            'Неверное имя пользователя или пароль'
        } else {
          this.errorMessage =
            'Не удалось подключиться к серверу'
        }
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;

  background:
    linear-gradient(
      135deg,
      #0f172a 0%,
      #1e3a8a 50%,
      #2563eb 100%
    );
}

.login-card {
  backdrop-filter: blur(20px);


  border: 1px solid rgba(255, 255, 255, 0.15);

  border-radius: 24px !important;

  box-shadow:
    0 20px 60px rgba(0, 0, 0, 0.35) !important;
}

.logo-wrapper {
  width: 110px;
  height: 110px;

  margin: 0 auto;

  border-radius: 50%;

  display: flex;
  align-items: center;
  justify-content: center;

  background:
    linear-gradient(
      135deg,
      #2563eb,
      #3b82f6
    );

  box-shadow:
    0 10px 30px rgba(37, 99, 235, 0.4);
}

.login-btn {
  height: 52px !important;

  font-size: 15px;
  font-weight: 600;

  text-transform: none;

  border-radius: 12px !important;
}

.login-btn:hover {
  transform: translateY(-1px);
}

.fill-height {
  min-height: 100vh;
}
</style>
```
