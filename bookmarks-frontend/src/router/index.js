import { createRouter, createWebHistory } from 'vue-router'
import SignUpView from '@/views/signup.vue'
import CreateUserBooksView from '@/views/createuser.vue'
import CreateUserWriterView from '@/views/createwriter.vue'
import LoggedInView from '@/views/LoggedInReader.vue'
import ReviewPage from '@/components/feed/ReviewPage.vue'

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
      path: '/feed/:user',
      name: 'feed',
      component: LoggedInView,
      children: [
        {
        path: 'review/:review',
        component: ReviewPage
        }
      ]
    },
    {
      path: '/home/:writer',
      name: 'writersDesk'
    }
  ]
})

export default router
