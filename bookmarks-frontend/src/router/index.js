import { createRouter, createWebHistory } from 'vue-router';
import SignUpView from '@/views/signup.vue';
import CreateUserBooksView from '@/views/createuser.vue';
import CreateUserWriterView from '@/views/createwriter.vue';
import LoggedInView from '@/views/LoggedInReader.vue';
import commentsPage from '@/components/feed/commentsPage.vue';
import WorkFeed from '@/components/feed/WorkFeed.vue';
import WorkPage from '@/components/feed/WorkPage.vue';
import AuthorPage from '@/components/feed/authors/AuthorPage.vue';
import SearchPage from '@/components/feed/navigation/SearchPage.vue';
import SocialPage from '@/components/feed/social/SocialPage.vue';
import SettingsPage from '@/components/feed/SettingsPage.vue';
import UserPage from '@/components/feed/UserPage.vue';
import BookshelvesPage from '@/components/feed/BookshelvesPage.vue';
import ViewBookshelf from '@/components/feed/bookshelves/ViewBookshelf.vue';
import EditBookshelfSettings from '@/components/feed/bookshelves/EditBookshelfSettings.vue';
import BookshelvesMain from '@/components/feed/bookshelves/BookshelvesMain.vue';
import ViewBookshelvesBySection from '@/components/feed/bookshelves/ViewBookshelvesBySection.vue';
import CreateBookshelfForm from '@/components/feed/bookshelves/CreateBookshelf.vue';
import CreatePostPage from '@/components/feed/CreatePostPage.vue';
import BookClubsIndex from '@/components/feed/bookclubs/BookClubsIndex.vue';
import CreateBookClubs from '@/components/feed/bookclubs/create/CreateBookClubs.vue';
import BookClubsHome from '@/components/feed/bookclubs/home/BookClubsHome.vue';
import BookClub from '@/components/feed/bookclubs/club/BookClub.vue';
import CreateUserFromBookClubInvite from '@/views/CreateUserFromBookClubInvite.vue';

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
      component: CreateUserBooksView,
    },
    {
      path: '/create-user-writer',
      name: 'CreateWriter',
      component: CreateUserWriterView,
    },
    {
      path: '/invite/:inviteId',
      name: 'BookClubInvitedFlow',
      component: CreateUserFromBookClubInvite,
    },
    {
      // We need router here.
      name: 'feed',
      path: '/feed/:user',
      component: LoggedInView,
      children: [
        {
          name: 'home-feed',
          path: 'all',
          component: WorkFeed,
        },
        {
          name: 'post-page',
          path: 'post/:post',
          component: commentsPage,
        },
        {
          name: 'settings',
          path: 'settings',
          component: SettingsPage,
        },
        {
          // canonical
          name: 'work-page',
          path: 'works/:work',
          component: WorkPage,
          children: [
            {
              //feed/:user_uuid/work/:work_uuid/version/:versiun_uuid
              name: 'work-versions-page',
              path: 'version/:version_uuid',
              component: WorkPage,
            }
          ]
        },
        {
          name: 'user-profile-page',
          path: 'user/:user_profile',
          component: UserPage,
        },
        {
          name: 'create-post',
          path: 'create/:reviewType/:bookID?',
          component: CreatePostPage,
        },
        {
          path: 'authors/:author',
          component: AuthorPage,
        },
        {
          path: 'search',
          component: SearchPage,
        },
        {
          path: 'social',
          component: SocialPage,
        },
        {
          path: 'bookshelves',
          component: BookshelvesPage,
          children: [
            {
              path: 'by/:shelfType',
              component: ViewBookshelvesBySection
            },
            {
              path: ':bookshelf',
              component: ViewBookshelf,
            },
            {
              path: ':bookshelf/edit',
              component: EditBookshelfSettings,
            },
            {
              path: 'all',
              name: 'bookshelves-home',
              component: BookshelvesMain,
            },
            {
              path: 'create',
              component: CreateBookshelfForm,
            },
          ]
        },
        {
          path: 'bookclubs',
          component: BookClubsIndex,
          children: [
            {
              path: '',
              name: 'bookclubs-home',
              component: BookClubsHome
            },
            {
              path: 'create',
              component: CreateBookClubs,
            },
            {
              path: ':bookclub',
              component: BookClub,
              children: [
                {
                  path: 'feed',
                  name: 'clubFeed',
                },
                {
                  path: 'post/:postId',
                  name: 'clubCommentPage',
                },
                {
                  path: 'post/:postId/comments/:threadId',
                  name: 'clubCommentsSubThreadPage',
                },
                {
                  path: 'settings/currently-reading',
                  name: 'currentlyReading'
                },
                {
                  path: 'settings/manage-members',
                  name: 'manageMembers',
                }
              ]
            }
          ]
        },
      ]
    },
    {
      path: '/home/:writer',
      name: 'writersDesk',
    },
  ]
})

export default router
