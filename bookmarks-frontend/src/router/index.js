import { createRouter, createWebHistory } from 'vue-router'
import SignUpView from '@/views/signup.vue'
import CreateUserBooksView from '@/views/createuser.vue'
import CreateUserWriterView from '@/views/createwriter.vue'
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
      path: '/create-user-writer',
      name: 'CreateWriter',
      component: CreateUserWriterView
    },
    {
      // We need router here.
      path: '/home/:user',
      name: 'BookShelf',
      component: BookShelfView
    },
    {
      path: '/home/:writer',
      name: 'writersDesk'
    }
  ]
})

export default router
