import { createRouter, createWebHistory } from 'vue-router'
import SignUpView from '@/views/signup.vue'
import CreateUserBooksView from '@/views/createuser.vue'
import BookShelfView from '@/views/bookshelf.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'SignUp',
      component: SignUpView
    },
    {
      path: '/create-user',
      name: 'CreateUser',
      component: CreateUserBooksView
    },
    {
      // We need router here.
      path: '/home/:user',
      name: 'BookShelf',
      component: BookShelfView
    }
  ]
})

export default router
