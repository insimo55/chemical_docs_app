// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import ReagentsListView from '../views/ReagentsListView.vue'
import ReagentDetailView from '../views/ReagentDetailView.vue'
import UsersListView from '../views/UsersListView.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: LoginView,
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    name: 'ReagentsList',
    component: ReagentsListView,
    meta: { requiresAuth: true }
  },
  {
    path: '/reagent/:id',
    name: 'ReagentDetail',
    component: ReagentDetailView,
    meta: { requiresAuth: true }
  },
  // Перенаправление на главную при вводе несуществующего пути
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  },
  {
    path: '/users',
    name: 'UsersList',
    component: UsersListView,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Проверка авторизации перед каждым переходом
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')

  if (to.meta.requiresAuth && !token) {
    // Если страница требует авторизации, а токена нет — отправляем на логин
    next('/login')
  } else if (to.name === 'Login' && token) {
    // Если авторизованный пользователь пытается зайти на страницу логина — отправляем на главную
    next('/')
  } else {
    next()
  }
})

export default router