<!-- src/views/ReagentDetailView.vue -->
<template>
  <div>
    <!-- Верхняя панель навигации -->
    <v-app-bar color="primary" density="compact" elevation="2">
      <v-btn icon @click="goBack">
        <v-icon>mdi-arrow-left</v-icon>
      </v-btn>
      <v-app-bar-title class="font-weight-bold">
        Редактирование реагента
      </v-app-bar-title>
    </v-app-bar>

    <v-container class="mt-4" v-if="loading">
      <v-row justify="center" class="my-12">
        <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
      </v-row>
    </v-container>

    <v-container class="mt-4" v-else-if="reagent">
      <v-row>
        <!-- Левая колонка: Информация о реагенте и редактирование -->
        <v-col cols="12" md="5">
          <v-card class="rounded-lg pa-4 elevation-2 mb-4">
            <v-card-item class="pb-0">
              <v-card-title class="text-h6 font-weight-bold mb-1">Данные реагента</v-card-title>
            </v-card-item>

            <v-card-text class="pt-4">
              <v-form ref="editForm" v-model="isEditFormValid">
                <v-text-field
                  v-model="reagent.name"
                  label="Название реагента *"
                  :rules="[v => !!v || 'Название обязательно']"
                  variant="outlined"
                  required
                ></v-text-field>

                <v-text-field
                  v-model="reagent.manufacturer"
                  label="Производитель"
                  variant="outlined"
                ></v-text-field>

                <v-textarea
                  v-model="reagent.description"
                  label="Описание"
                  variant="outlined"
                  rows="4"
                ></v-textarea>

                <v-btn
                  color="primary"
                  block
                  :disabled="!isEditFormValid"
                  :loading="savingReagent"
                  @click="updateReagent"
                  class="text-none mb-3"
                >
                  Сохранить изменения
                </v-btn>

                <v-divider class="my-4"></v-divider>

                <v-btn
                  color="error"
                  variant="outlined"
                  block
                  @click="deleteReagent"
                  class="text-none"
                  prepend-icon="mdi-trash-can-outline"
                >
                  Удалить реагент
                </v-btn>
              </v-form>
            </v-card-text>
          </v-card>
        </v-col>

        <!-- Правая колонка: Управление документами -->
        <v-col cols="12" md="7">
          <!-- Загрузка нового документа -->
          <v-card class="rounded-lg pa-4 elevation-2 mb-6">
            <v-card-item class="pb-0">
              <v-card-title class="text-h6 font-weight-bold">Загрузить документ</v-card-title>
            </v-card-item>

            <v-card-text class="pt-4">
              <v-form ref="uploadForm" v-model="isUploadFormValid">
                <v-file-input
                  v-model="fileToUpload"
                  label="Выбрать файл *"
                  :rules="[v => !!v || 'Выберите файл для загрузки']"
                  variant="outlined"
                  prepend-icon=""
                  prepend-inner-icon="mdi-paperclip"
                  show-size
                  required
                  @update:modelValue="onFileSelected"
                ></v-file-input>

                <v-text-field
                  v-model="newDoc.name"
                  label="Название документа *"
                  :rules="[v => !!v || 'Введите понятное название']"
                  variant="outlined"
                  required
                ></v-text-field>

                <v-row>
                  <v-col cols="12" sm="6">
                    <v-select
                      v-model="newDoc.document_type"
                      label="Тип документа *"
                      :items="documentTypes"
                      variant="outlined"
                      required
                    ></v-select>
                  </v-col>
                  <v-col cols="12" sm="6">
                    <!-- Будем использовать обычный input date, так как во Vuetify 3 еще нет стабильного универсального DatePicker из коробки -->
                    <v-text-field
                      v-model="newDoc.valid_from"
                      label="Действует с"
                      type="date"
                      variant="outlined"
                    ></v-text-field>
                  </v-col>
                </v-row>

                <v-row class="mt-n4">
                  <v-col cols="12" sm="6">
                    <v-text-field
                      v-model="newDoc.valid_until"
                      label="Действует до"
                      type="date"
                      variant="outlined"
                    ></v-text-field>
                  </v-col>
                  <v-col cols="12" sm="6" class="d-flex align-center">
                    <v-checkbox
                      v-model="newDoc.is_active"
                      label="Документ активен"
                      hide-details
                    ></v-checkbox>
                  </v-col>
                </v-row>

                <v-btn
                  color="success"
                  block
                  :disabled="!isUploadFormValid || !fileToUpload"
                  :loading="uploadingFile"
                  @click="uploadDocument"
                  class="text-none mt-2"
                  prepend-icon="mdi-upload"
                >
                  Загрузить на сервер
                </v-btn>
              </v-form>
            </v-card-text>
          </v-card>

          <!-- Список текущих документов -->
          <v-card class="rounded-lg pa-4 elevation-2">
            <v-card-title class="text-h6 font-weight-bold mb-4">Текущие документы</v-card-title>
            
            <div v-if="reagent.documents && reagent.documents.length > 0">
              <v-list lines="two" class="bg-transparent">
                <v-list-item
                  v-for="doc in reagent.documents"
                  :key="doc.id"
                  class="border-sm rounded-lg mb-2 pa-3"
                >
                  <template v-slot:prepend>
                    <v-icon color="primary" size="large" class="mr-3">mdi-file-document-outline</v-icon>
                  </template>

                  <v-list-item-title class="font-weight-medium text-body-1">
                    {{ doc.name }}
                  </v-list-item-title>
                  
                  <v-list-item-subtitle class="text-caption mt-1">
                    Тип: <strong>{{ doc.document_type }}</strong> | {{ formatValidityPeriod(doc.valid_from, doc.valid_until) }}
                    <v-chip
                      size="x-small"
                      :color="doc.validity_status === 'Active' || doc.validity_status === 'Active (perpetual)' ? 'success' : doc.validity_status === 'Expires soon' ? 'warning' : 'error'"
                      class="ml-2"
                    >
                      {{ getStatusText(doc.validity_status) }}
                    </v-chip>
                  </v-list-item-subtitle>

                  <template v-slot:append>
                    <v-btn
                      icon="mdi-download"
                      variant="text"
                      color="primary"
                      @click="downloadDocument(doc.id, doc.name, doc.file_path)"
                      title="Скачать"
                    ></v-btn>
                    <v-btn
                      icon="mdi-trash-can-outline"
                      variant="text"
                      color="error"
                      @click="deleteDocument(doc.id)"
                      title="Удалить"
                    ></v-btn>
                  </template>
                </v-list-item>
              </v-list>
            </div>
            <v-alert v-else type="info" variant="tonal" class="rounded-lg">
              Документы не загружены. Используйте форму выше для загрузки.
            </v-alert>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script>
import api from '../utils/api'

export default {
  name: 'ReagentDetailView',
  data() {
    return {
      reagent: null,
      loading: true,
      savingReagent: false,
      isEditFormValid: false,

      // Загрузка файла
      fileToUpload: null,
      isUploadFormValid: false,
      uploadingFile: false,
      documentTypes: [
        'ГОСТ',
        'ТУ',
        'Паспорт безопасности (MSDS)',
        'Сертификат соответствия',
        'Паспорт партии',
        'Протокол испытания ХОС',
        'Другое'
      ],
      newDoc: {
        name: '',
        document_type: 'Другое',
        valid_from: '',
        valid_until: '',
        is_active: true
      }
    }
  },
  mounted() {
    this.fetchReagentDetails()
  },
  methods: {
    async fetchReagentDetails() {
      this.loading = true
      const id = this.$route.params.id
      try {
        const response = await api.get(`/reagents/${id}`)
        this.reagent = response.data
      } catch (error) {
        console.error('Ошибка загрузки деталей реагента:', error)
        this.goBack()
      } finally {
        this.loading = false
      }
    },
    async updateReagent() {
      if (!this.isEditFormValid) return
      this.savingReagent = true
      try {
        await api.put(`/reagents/${this.reagent.id}`, {
          name: this.reagent.name,
          manufacturer: this.reagent.manufacturer,
          description: this.reagent.description
        })
        alert('Данные реагента успешно обновлены!')
      } catch (error) {
        console.error('Ошибка обновления реагента:', error)
      } finally {
        this.savingReagent = false
      }
    },
    async deleteReagent() {
      if (!confirm('Вы действительно хотите удалить этот реагент и все связанные с ним документы? Это действие необратимо.')) return
      try {
        await api.delete(`/reagents/${this.reagent.id}`)
        this.goBack()
      } catch (error) {
        console.error('Ошибка удаления реагента:', error)
      }
    },
    onFileSelected(file) {
      if (file && !this.newDoc.name) {
        // Автоматически подставляем имя файла без расширения в название документа
        const nameWithoutExt = file.name.substring(0, file.name.lastIndexOf('.')) || file.name
        this.newDoc.name = nameWithoutExt
      }
    },
    async uploadDocument() {
      if (!this.isUploadFormValid || !this.fileToUpload) return
      this.uploadingFile = true

      // Для отправки файлов необходимо использовать FormData
      const formData = new FormData()
      formData.append('file', this.fileToUpload)
      formData.append('name', this.newDoc.name)
      formData.append('document_type', this.newDoc.document_type)
      
      if (this.newDoc.valid_from) formData.append('valid_from', this.newDoc.valid_from)
      if (this.newDoc.valid_until) formData.append('valid_until', this.newDoc.valid_until)
      formData.append('is_active', this.newDoc.is_active)

      try {
        await api.post(`/documents/upload/${this.reagent.id}`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })
        
        // Сбрасываем форму
        this.fileToUpload = null
        this.newDoc = {
          name: '',
          document_type: 'Другое',
          valid_from: '',
          valid_until: '',
          is_active: true
        }
        if (this.$refs.uploadForm) this.$refs.uploadForm.resetValidation()
        
        // Перезапрашиваем данные реагента, чтобы обновить список документов
        await this.fetchReagentDetails()
      } catch (error) {
        console.error('Ошибка загрузки документа:', error)
      } finally {
        this.uploadingFile = false
      }
    },
    async downloadDocument(docId, docName, filePath) {
      try {
        const response = await api.get(`/documents/download/${docId}`, {
          responseType: 'blob'
        })
        // Получаем расширение
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
        console.error('Ошибка скачивания:', error)
      }
    },
    async deleteDocument(docId) {
      if (!confirm('Вы уверены, что хотите удалить этот документ с сервера?')) return
      try {
        await api.delete(`/documents/${docId}`)
        await this.fetchReagentDetails() // Обновляем список документов
      } catch (error) {
        console.error('Ошибка удаления документа:', error)
      }
    },
    goBack() {
      this.$router.push('/')
    },
    formatValidityPeriod(from, until) {
      if (!from && !until) return 'Бессрочный'
      const f = from ? new Date(from).toLocaleDateString('ru-RU') : '...'
      const u = until ? new Date(until).toLocaleDateString('ru-RU') : 'бессрочно'
      return `Действует с ${f} по ${u}`
    },
    getStatusText(status) {
      switch (status) {
        case 'Active': return 'Активен'
        case 'Active (perpetual)': return 'Бессрочно'
        case 'Expires soon': return 'Истекает скоро'
        case 'Expired': return 'Истек'
        default: return 'Неизвестно'
      }
    }
  }
}
</script>