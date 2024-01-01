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
import CreateReviewPage from '@/components/feed/CreateReviewPage.vue';
import SettingsPage from '@/components/feed/SettingsPage.vue';
import UserPage from '@/components/feed/UserPage.vue';
import BookshelvesPage from '@/components/feed/BookshelvesPage.vue';

export const router = createRouter({
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
          path: 'settings',
          component: SettingsPage
        },
        {
          // canonical
          path: 'works/:work',
          component: WorkPage,
          children: [
            {
              //feed/:user_uuid/work/:work_uuid/version/:versiun_uuid
              path: 'version/:version_uuid',
              component: WorkPage
            }
          ]
        },
        {
          path: 'user/:user_profile',
          component: UserPage,
        },
        {
          path: 'create/review/:reviewType/work/:work1',
          component: CreateReviewPage
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
          path: 'social',
          component: SocialPage
        },
        {
          path: 'bookshelves/:bookshelf',
          component: BookshelvesPage
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
