// src/plugins/vuetify.js
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import '@mdi/font/css/materialdesignicons.css' // Подключаем иконки

export default createVuetify({
  components,
  directives,
  theme: {
    defaultTheme: 'light',
    themes: {
      light: {
        colors: {
          primary: '#1976D2',    // Синий цвет для основных кнопок и элементов
          secondary: '#424242',  // Темно-серый
          accent: '#82B1FF',
          error: '#FF5252',      // Красный для просроченных документов
          info: '#2196F3',
          success: '#4CAF50',    // Зеленый для активных документов
          warning: '#FB8C00',    // Оранжевый для истекающих документов
        },
      },
    },
  },
})