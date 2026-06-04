<!-- src/views/ReagentsListView.vue -->
<template>
  <div>
    <!-- Верхняя панель навигации -->
    <v-app-bar color="primary" density="compact" elevation="2">
      <v-app-bar-title class="font-weight-bold">
        <v-icon class="mr-2">mdi-flask-outline</v-icon>
        Учет хим. реагентов
      </v-app-bar-title>
      <v-spacer></v-spacer>
      <v-btn icon @click="goToUsers" class="mr-2" title="Управление пользователями">
        <v-icon>mdi-account-group</v-icon>
      </v-btn>
      <v-btn icon @click="logout" title="Выйти из системы">
        <v-icon>mdi-logout</v-icon>
      </v-btn>
    </v-app-bar>

    <v-container class="mt-4">
      <!-- Блок поиска и добавления нового реагента -->
      <v-row align="center" class="mb-4">
        <v-col cols="12" sm="8" md="6">
          <v-text-field
            v-model="searchQuery"
            label="Поиск реагента по названию..."
            prepend-inner-icon="mdi-magnify"
            variant="outlined"
            density="comfortable"
            hide-details
            clearable
          ></v-text-field>
        </v-col>
        <v-col cols="12" sm="4" md="6" class="text-sm-right">
          <v-btn
            color="success"
            prepend-icon="mdi-plus"
            @click="showAddDialog = true"
            class="text-none"
            size="large"
          >
            Добавить реагент
          </v-btn>
        </v-col>
      </v-row>

      <!-- Панель пакетного скачивания для тендера -->
      <v-expand-transition>
        <v-card v-if="selectedReagents.length > 0" color="blue-lighten-5" class="mb-6 pa-4 rounded-lg">
          <v-row align="center">
            <v-col cols="12" sm="8">
              <span class="text-subtitle-1 font-weight-medium">
                Выбрано реагентов для тендера: <strong>{{ selectedReagents.length }}</strong>
              </span>
            </v-col>
            <v-col cols="12" sm="4" class="text-sm-right">
              <v-btn
                color="primary"
                prepend-icon="mdi-zip-box"
                :loading="batchDownloading"
                @click="downloadBatch"
                class="text-none"
              >
                Скачать пакет документов
              </v-btn>
            </v-col>
          </v-row>
        </v-card>
      </v-expand-transition>

      <!-- Индикатор загрузки списка -->
      <v-row v-if="loadingList" justify="center" class="my-8">
        <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
      </v-row>

      <!-- Список реагентов (аккордеон) -->
      <v-card v-else-if="filteredReagents.length > 0" class="rounded-lg elevation-2">
        <v-expansion-panels variant="accordion">
          <v-expansion-panel
            v-for="reagent in filteredReagents"
            :key="reagent.id"
          >
            <!-- Заголовок аккордеона -->
            <v-expansion-panel-title class="py-3">
              <template v-slot:default="{ expanded }">
                <v-row no-gutters align="center" class="w-100">
                  <!-- Чекбокс для выбора -->
                  <v-col cols="auto" class="mr-2">
                    <v-checkbox
                      v-model="selectedReagents"
                      :value="reagent.id"
                      hide-details
                      density="compact"
                      @click.stop
                    ></v-checkbox>
                  </v-col>
                  
                  <!-- Название реагента -->
                  <v-col class="text-subtitle-1 font-weight-bold">
                    {{ reagent.name }}
                  </v-col>

                  <!-- Производитель -->
                  <v-col cols="12" md="3" class="text-grey text-body-2 mt-1 mt-md-0">
                    <v-icon size="small" class="mr-1">mdi-factory</v-icon>
                    {{ reagent.manufacturer || 'Не указан' }}
                  </v-col>

                  <!-- Статус актуальности документов -->
                  <v-col cols="12" md="3" class="text-right pr-4 mt-1 mt-md-0">
                    <v-chip
                      :color="getStatusColor(reagent.validity_status)"
                      size="small"
                      class="font-weight-medium"
                    >
                      {{ getStatusText(reagent.validity_status, reagent.min_valid_until) }}
                    </v-chip>
                  </v-col>
                </v-row>
              </template>
            </v-expansion-panel-title>

            <!-- Содержимое аккордеона -->
            <v-expansion-panel-text class="bg-grey-lighten-5">
              <div class="py-2">
                <p class="text-body-2 text-grey-darken-2 mb-4">
                  <strong>Описание:</strong> {{ reagent.description || 'Описание отсутствует.' }}
                </p>

                <h4 class="text-subtitle-2 mb-2 font-weight-bold">Документы реагента:</h4>
                
                <!-- Запрос документов реагента -->
                <div v-if="reagent.documents && reagent.documents.length > 0">
                  <v-table density="compact" class="bg-transparent">
                    <thead>
                      <tr>
                        <th class="text-left">Название документа</th>
                        <th class="text-left">Тип</th>
                        <th class="text-left">Срок действия</th>
                        <th class="text-right">Действие</th>
                      </tr>
                    </thead>
                    <tbody>
                      <v-row v-if="!reagent.documents" justify="center">
                        <v-progress-circular indeterminate size="24" class="my-2"></v-progress-circular>
                      </v-row>
                      <tr v-for="doc in reagent.documents" :key="doc.id">
                        <td>{{ doc.name }}</td>
                        <td>
                          <v-chip size="x-small" variant="outlined">{{ doc.document_type }}</v-chip>
                        </td>
                        <td>
                          <span :class="doc.validity_status === 'Expired' ? 'text-red font-weight-bold' : ''">
                            {{ formatValidityPeriod(doc.valid_from, doc.valid_until) }}
                          </span>
                        </td>
                        <td class="text-right">
                          <v-btn
                            icon="mdi-download"
                            size="x-small"
                            variant="text"
                            color="primary"
                            @click="downloadSingleDocument(doc.id, doc.name, doc.file_path)"
                            title="Скачать документ"
                          ></v-btn>
                        </td>
                      </tr>
                    </tbody>
                  </v-table>
                </div>
                <v-alert v-else type="info" variant="tonal" density="compact" class="text-caption mb-4">
                  Для данного реагента еще не загружено ни одного документа.
                </v-alert>

                <v-divider class="my-3"></v-divider>

                <!-- Кнопка перехода к редактированию -->
                <v-btn
                  color="primary"
                  variant="outlined"
                  size="small"
                  prepend-icon="mdi-cog-outline"
                  @click="goToDetail(reagent.id)"
                  class="text-none"
                >
                  Настроить реагент / Добавить документы
                </v-btn>
              </div>
            </v-expansion-panel-text>
          </v-expansion-panel>
        </v-expansion-panels>
      </v-card>

      <!-- Если ничего не найдено -->
      <v-alert v-else type="warning" variant="tonal" class="rounded-lg">
        Реагенты не найдены. Создайте новый реагент, используя кнопку «Добавить реагент».
      </v-alert>
    </v-container>

    <!-- Модальное окно добавления реагента -->
    <v-dialog v-model="showAddDialog" max-width="500px">
      <v-card class="rounded-lg">
        <v-card-title class="bg-primary text-white font-weight-bold">
          Добавить химический реагент
        </v-card-title>
        <v-card-text class="pt-4">
          <v-form ref="addForm" v-model="isAddFormValid">
            <v-text-field
              v-model="newReagent.name"
              label="Название реагента *"
              :rules="[v => !!v || 'Название обязательно к заполнению']"
              variant="outlined"
              required
            ></v-text-field>

            <v-text-field
              v-model="newReagent.manufacturer"
              label="Производитель"
              variant="outlined"
            ></v-text-field>

            <v-textarea
              v-model="newReagent.description"
              label="Описание реагента"
              variant="outlined"
              rows="3"
            ></v-textarea>
          </v-form>
        </v-card-text>
        <v-card-actions class="justify-end pb-4 pr-4">
          <v-btn variant="text" @click="closeAddDialog" class="text-none">Отмена</v-btn>
          <v-btn
            color="success"
            variant="flat"
            :disabled="!isAddFormValid"
            :loading="addingReagent"
            @click="submitReagent"
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
  name: 'ReagentsListView',
  data() {
    return {
      searchQuery: '',
      reagents: [],
      selectedReagents: [],
      loadingList: false,
      batchDownloading: false,
      
      // Добавление реагента
      showAddDialog: false,
      isAddFormValid: false,
      addingReagent: false,
      newReagent: {
        name: '',
        manufacturer: '',
        description: ''
      }
    }
  },
  computed: {
    filteredReagents() {
      if (!this.searchQuery) return this.reagents
      const query = this.searchQuery.toLowerCase()
      return this.reagents.filter(r => r.name.toLowerCase().includes(query))
    }
  },
  mounted() {
    this.fetchReagents()
  },
  methods: {
    async fetchReagents() {
      this.loadingList = true
      try {
        const response = await api.get('/reagents/')
        const reagentsList = response.data
        
        // Для каждого реагента подгрузим список его документов, чтобы отображать в аккордеоне
        for (let reagent of reagentsList) {
          try {
            const detailResponse = await api.get(`/reagents/${reagent.id}`)
            reagent.documents = detailResponse.data.documents
          } catch (e) {
            reagent.documents = []
          }
        }
        
        this.reagents = reagentsList
      } catch (error) {
        console.error('Ошибка получения списка реагентов:', error)
      } finally {
        this.loadingList = false
      }
    },
    async submitReagent() {
      if (!this.isAddFormValid) return
      this.addingReagent = true
      try {
        await api.post('/reagents/', this.newReagent)
        this.closeAddDialog()
        this.fetchReagents() // Обновляем список
      } catch (error) {
        console.error('Ошибка добавления реагента:', error)
      } finally {
        this.addingReagent = false
      }
    },
    closeAddDialog() {
      this.showAddDialog = false
      this.newReagent = { name: '', manufacturer: '', description: '' }
      if (this.$refs.addForm) this.$refs.addForm.resetValidation()
    },
    async downloadSingleDocument(docId, docName, filePath) {
      try {
        const response = await api.get(`/documents/download/${docId}`, {
          responseType: 'blob'
        })
        const extension = filePath.split('.').pop()
        const downloadName = docName.endsWith(`.${extension}`) ? docName : `${docName}.${extension}`
        
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', downloadName)
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
      } catch (error) {
        console.error('Ошибка скачивания документа:', error)
      }
    },
    async downloadBatch() {
      if (this.selectedReagents.length === 0) return
      this.batchDownloading = true
      try {
        const response = await api.post('/documents/download_batch', {
          reagent_ids: this.selectedReagents
        }, {
          responseType: 'blob'
        })
        
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', 'tender_documents.zip')
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
      } catch (error) {
        console.error('Ошибка пакетного скачивания:', error)
      } finally {
        this.batchDownloading = false
      }
    },
    goToDetail(id) {
      this.$router.push(`/reagent/${id}`)
    },
    goToUsers() {
  this.$router.push('/users')
},
    logout() {
      localStorage.removeItem('token')
      this.$router.push('/login')
    },
    getStatusColor(status) {
      switch (status) {
        case 'Active': return 'success'
        case 'Active (perpetual)': return 'success'
        case 'Expires soon': return 'warning'
        case 'Expired': return 'error'
        default: return 'grey'
      }
    },
    getStatusText(status, dateStr) {
      const formattedDate = dateStr ? new Date(dateStr).toLocaleDateString('ru-RU') : ''
      switch (status) {
        case 'Active': return `Активен до ${formattedDate}`
        case 'Active (perpetual)': return 'Бессрочно активен'
        case 'Expires soon': return `Истекает скоро (${formattedDate})`
        case 'Expired': return `Просрочен (${formattedDate})`
        case 'No active documents': return 'Нет активных документов'
        default: return 'Статус неизвестен'
      }
    },
    formatValidityPeriod(from, until) {
      if (!from && !until) return 'Бессрочно'
      const f = from ? new Date(from).toLocaleDateString('ru-RU') : '...'
      const u = until ? new Date(until).toLocaleDateString('ru-RU') : 'бессрочно'
      return `с ${f} по ${u}`
    }
  }
}
</script>