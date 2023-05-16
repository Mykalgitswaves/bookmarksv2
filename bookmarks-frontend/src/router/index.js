import { createRouter, createWebHistory } from 'vue-router'
import SignUpView from '@/views/signup.vue';
import CreateUserBooksView from '@/views/createuser.vue';


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
      component: CreateUserBooksView,
        children: [
          { 
            path: '',
            name: 'createformbooksearch',
            component: () => import('../components/create/createuserformbooks.vue')
          },
          {
            path: '',
            name: 'createformgenres',
            component: () => import('../components/create/createusergenre.vue')
          }
        ]
    },
  ]
})

export default router
