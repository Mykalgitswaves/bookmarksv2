import { createRouter, createWebHistory } from 'vue-router'
import SignUpView from '@/views/signup.vue'
import CreateUserBooksView from '@/views/createuser.vue'
import CreateUserWriterView from '@/views/createwriter.vue'
import LoggedInView from '@/views/LoggedInReader.vue'
import commentsPage from '@/components/feed/commentsPage.vue'
import WorkFeed from '@/components/feed/WorkFeed.vue'
import WorkPage from '@/components/feed/WorkPage.vue'
import AuthorPage from '@/components/feed/authors/AuthorPage.vue';
import SearchPage from '@/components/feed/navigation/SearchPage.vue';
import SocialPage from '@/components/feed/social/SocialPage.vue';

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
          path: 'all',
          component: WorkFeed,
        },
        {
          path: 'post/:post',
          component: commentsPage,
        },
        {
          path: 'works/:work',
          component: WorkPage
        },
        {
          path: 'authors/:author',
          component: AuthorPage
        },
        {
          path: 'search',
          component: SearchPage
        },
        {
          path: 'social/',
          component: SocialPage
        }
      ]
    },
    {
      path: '/home/:writer',
      name: 'writersDesk'
    },
  ]
})

export default router
