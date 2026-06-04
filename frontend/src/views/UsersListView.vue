<!-- src/views/UsersListView.vue -->
<template>
  <div>
    <!-- Верхняя панель навигации -->
    <v-app-bar color="primary" density="compact" elevation="2">
      <v-btn icon @click="goToReagents" title="К списку реагентов">
        <v-icon>mdi-arrow-left</v-icon>
      </v-btn>
      <v-app-bar-title class="font-weight-bold">
        Управление пользователями
      </v-app-bar-title>
    </v-app-bar>

    <v-container class="mt-4">
      <!-- Заголовок и кнопка добавления -->
      <v-row align="center" class="mb-4">
        <v-col cols="12" sm="6">
          <h2 class="text-h5 font-weight-bold text-grey-darken-3">Список учетных записей</h2>
        </v-col>
        <v-col cols="12" sm="6" class="text-sm-right">
          <v-btn
            color="success"
            prepend-icon="mdi-account-plus"
            @click="openAddDialog"
            class="text-none"
          >
            Добавить пользователя
          </v-btn>
        </v-col>
      </v-row>

      <!-- Индикатор загрузки -->
      <v-row v-if="loading" justify="center" class="my-8">
        <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
      </v-row>

      <!-- Таблица пользователей -->
      <v-card v-else class="rounded-lg elevation-2">
        <v-table>
          <thead>
            <tr>
              <th class="text-left font-weight-bold">Имя пользователя</th>
              <th class="text-left font-weight-bold">Электронная почта</th>
              <th class="text-left font-weight-bold">Дата регистрации</th>
              <th class="text-right font-weight-bold pr-6">Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in users" :key="user.id">
              <td class="font-weight-medium">{{ user.username }}</td>
              <td>{{ user.email || '—' }}</td>
              <td>{{ formatDate(user.created_at) }}</td>
              <td class="text-right pr-4">
                <!-- Редактировать -->
                <v-btn
                  icon="mdi-pencil-outline"
                  variant="text"
                  color="primary"
                  size="small"
                  @click="openEditDialog(user)"
                  title="Редактировать / Сменить пароль"
                  class="mr-1"
                ></v-btn>
                <!-- Удалить -->
                <v-btn
                  icon="mdi-delete-outline"
                  variant="text"
                  color="error"
                  size="small"
                  @click="deleteUser(user.id, user.username)"
                  title="Удалить пользователя"
                ></v-btn>
              </td>
            </tr>
          </tbody>
        </v-table>
      </v-card>
    </v-container>

    <!-- Диалоговое окно Добавления/Редактирования -->
    <v-dialog v-model="showDialog" max-width="500px">
      <v-card class="rounded-lg">
        <v-card-title class="bg-primary text-white font-weight-bold">
          {{ isEditMode ? 'Редактировать пользователя' : 'Создать пользователя' }}
        </v-card-title>
        <v-card-text class="pt-4">
          <v-form ref="userForm" v-model="isFormValid">
            
            <v-text-field
              v-model="formData.username"
              label="Имя пользователя *"
              :rules="[v => !!v || 'Имя пользователя обязательно']"
              variant="outlined"
              required
            ></v-text-field>

            <v-text-field
              v-model="formData.email"
              label="Email"
              variant="outlined"
              type="email"
            ></v-text-field>

            <!-- Пароль: при редактировании он необязателен (если не хотят менять), при создании — обязателен -->
            <v-text-field
              v-model="formData.password"
              :label="isEditMode ? 'Новый пароль (оставьте пустым, если не хотите менять)' : 'Пароль *'"
              :rules="isEditMode ? [] : [v => !!v || 'Пароль обязателен']"
              variant="outlined"
              type="password"
              class="mb-2"
            ></v-text-field>
          </v-form>
          
          <v-alert v-if="errorMsg" type="error" variant="tonal" density="compact" class="text-caption">
            {{ errorMsg }}
          </v-alert>
        </v-card-text>
        <v-card-actions class="justify-end pb-4 pr-4">
          <v-btn variant="text" @click="closeDialog" class="text-none">Отмена</v-btn>
          <v-btn
            color="success"
            variant="flat"
            :disabled="!isFormValid"
            :loading="saving"
            @click="saveUser"
            class="text-none"
          >
            Сохранить
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import api from '../utils/api'

export default {
  name: 'UsersListView',
  data() {
    return {
      users: [],
      loading: false,
      saving: false,
      showDialog: false,
      isEditMode: false,
      isFormValid: false,
      errorMsg: '',

      formData: {
        id: null,
        username: '',
        email: '',
        password: ''
      }
    }
  },
  mounted() {
    this.fetchUsers()
  },
  methods: {
    async fetchUsers() {
      this.loading = true
      try {
        const response = await api.get('/auth/users')
        this.users = response.data
      } catch (error) {
        console.error('Ошибка получения пользователей:', error)
      } finally {
        this.loading = false
      }
    },
    openAddDialog() {
      this.isEditMode = false
      this.errorMsg = ''
      this.formData = { id: null, username: '', email: '', password: '' }
      this.showDialog = true
      if (this.$refs.userForm) this.$refs.userForm.resetValidation()
    },
    openEditDialog(user) {
      this.isEditMode = true
      this.errorMsg = ''
      this.formData = {
        id: user.id,
        username: user.username,
        email: user.email || '',
        password: '' // Оставляем пустым
      }
      this.showDialog = true
    },
    closeDialog() {
      this.showDialog = false
      this.errorMsg = ''
    },
    async saveUser() {
      if (!this.isFormValid) return
      this.saving = true
      this.errorMsg = ''

      try {
        if (this.isEditMode) {
          // Обновление пользователя
          await api.put(`/auth/users/${this.formData.id}`, {
            username: this.formData.username,
            email: this.formData.email,
            password: this.formData.password || null
          })
        } else {
          // Создание нового пользователя
          await api.post('/auth/users', {
            username: this.formData.username,
            email: this.formData.email,
            password: this.formData.password
          })
        }
        this.closeDialog()
        this.fetchUsers()
      } catch (error) {
        if (error.response && error.response.status === 409) {
          this.errorMsg = 'Пользователь с таким именем или email уже существует.'
        } else {
          this.errorMsg = 'Ошибка сохранения изменений.'
        }
        console.error(error)
      } finally {
        this.saving = false
      }
    },
    async deleteUser(userId, username) {
      if (!confirm(`Вы действительно хотите удалить пользователя "${username}"?`)) return
      try {
        await api.delete(`/auth/users/${userId}`)
        this.fetchUsers()
      } catch (error) {
        if (error.response && error.response.status === 400) {
          alert('Нельзя удалить единственного пользователя в системе.')
        } else {
          alert('Ошибка удаления пользователя.')
        }
        console.error(error)
      }
    },
    goToReagents() {
      this.$router.push('/')
    },
    formatDate(dateStr) {
      if (!dateStr) return '—'
      return new Date(dateStr).toLocaleDateString('ru-RU', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      })
    }
  }
}
</script>