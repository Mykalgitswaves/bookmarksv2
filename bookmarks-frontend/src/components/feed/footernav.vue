<template>
  <footer>
    <nav
      v-if="footerView === FooterViews.default"
      :class="{ minimized: minimizeFooter }"
      class="lg:border-solid border-indigo-100 border-[1px]"
      role="navigation"
    >
      <CreateMenu class="desktop-only w-100" />

      <div class="nav-menu-option w-100">
        <button
          class="space-y-2 flex items-center gap-2 text-sm fancy text-stone-600 hover:bg-stone-100 w-100 p-2"
          type="button"
          :disabled="$route.name === 'home-feed'"
          @click="goToFeedPage(user)"
        >
          <IconFeed style="width: 20px; height: 20px" />
          Feed
        </button>
      </div>

      <div class="nav-menu-option w-100">
        <button
          class="space-y-2 flex items-center gap-2 text-sm fancy text-stone-600 hover:bg-stone-100 w-100 p-2"
          typ="button"
          :disabled="$route.name === 'bookshelves-home'"
          @click="goToBookshelvesPage(user)"
        >
          <IconBookshelves style="width: 20px; height: 20px" />

          Bookshelves
        </button>
      </div>

      <div class="nav-menu-option w-100">
        <button
          class="space-y-2 flex items-center gap-2 text-sm fancy text-stone-600 hover:bg-stone-100 w-100 p-2"
          typ="button"
          :disabled="$route.name === 'bookclubs-home'"
          @click="goToBookClubsPage(user)"
        >
          <IconBookclubs style="width: 20px; height: 20px" />

          BookClubs
        </button>
      </div>

      <div class="nav-menu-option w-100">
        <button
          class="space-y-2 flex items-center gap-2 text-sm fancy text-stone-600 hover:bg-stone-100 w-100 p-2"
          typ="button"
          :disabled="$route.name === 'user'"
          @click="goToUserPage(user)"
        >
          <IconUser style="width: 20px; height: 20px" />

          Account
        </button>
      </div>
    </nav>

    <!-- Bookclub specific stuff -->
    <nav
      v-if="
        footerView === FooterViews.bookclubs && route.params['bookclub'] && !commentingForClubPost
      "
      :class="{ minimized: minimizeFooter }"
      class="lg:border-solid border-indigo-100 border-[1px]"
      role="navigation"
    >
      <div class="nav-menu-option w-100">
        <button
          class="space-y-2 flex items-center gap-2 text-sm fancy text-stone-600 hover:bg-stone-100 w-100 p-2"
          typ="button"
          @click="$router.push(navRoutes.toBookClubsPage($route.params.user))"
        >
          <IconBack style="width: 20px; height: 20px" />

          Back
        </button>
      </div>

      <div class="nav-menu-option w-100">
        <button
          class="space-y-2 flex items-center gap-2 text-sm fancy text-stone-600 hover:bg-stone-100 w-100 p-2"
          typ="button"
          @click="$router.push(navRoutes.toBookClubFeed(route.params.user, route.params.bookclub))"
        >
          <IconClubFeed style="width: 20px; height: 20px" />

          Feed
        </button>
      </div>

      <div class="nav-menu-option w-100">
        <button
          class="space-y-2 flex items-center gap-2 text-sm fancy text-stone-600 hover:bg-stone-100 w-100 p-2"
          typ="button"
          @click="
            $router.push(
              navRoutes.bookClubSettingsManageMembersIndex(route.params.user, route.params.bookclub)
            )
          "
        >
          <IconClubSettings style="width: 20px; height: 20px" />

          Settings
        </button>
      </div>

      <div class="nav-menu-option w-100">
        <button
          class="space-y-2 flex items-center gap-2 text-sm fancy text-stone-600 hover:bg-stone-100 w-100 p-2"
          typ="button"
          @click="
            $router.push(
              navRoutes.bookClubSettingsCurrentlyReading(route.params.user, route.params.bookclub)
            )
          "
        >
          <IconBook style="width: 20px; height: 20px" />

          Reading
        </button>
      </div>
    </nav>

    <!-- <nav
      v-if="
        footerView === FooterViews.bookclubs && route.params['bookclub'] && commentingForClubPost
      "
      class="club-comment-footer"
    >
      <p class="text-sm fancy" style="margin-left: 6%">
        Replying to
        <span class="text-indigo-500">{{ clubPostCommentMetaData.username }}'s</span>
      </p> -->

      <!-- <div class="comment-bar-section">
                <CommentBar
                    :post-id="clubPostCommentMetaData.post_id"
                    :comment="clubPostCommentMetaData"
                    @pre-success-comment="(comment) => PubSub.publish('footer-comment-pre-success-comment', {
                        commentId: clubPostCommentMetaData.id, 
                        reply: comment 
                    })" 
                    @post-failure-comment="(error) => PubSub.publish('footer-comment-failure-comment', { 
                        commentId: clubPostCommentMetaData.id,
                        error: error
                    })"
                />

                <button
                    type="button" 
                    class="btn btn-tiny btn-red mb-2"
                    @click="() => {
                        commentingForClubPost = false;
                        clubPostCommentMetaData = {};
                    }"
                >
                    <IconExit /> 
                </button>
            </div> -->
    <!-- </nav> -->
  </footer>

  <Transition name="content" tag="div">
    <div
      v-if="minimizeFooter && !commentingForClubPost"
      @click="minimizeFooter = false"
      @mouseover="minimizeFooter = false"
    >
      <div class="show-footer-nav">
        <span class="message">Show nav</span>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { useRoute, useRouter } from 'vue-router'
import { ref, computed } from 'vue'
// shad and other stuff
import CreateMenu from './footernav/CreateMenu.vue'
import IconBookclubs from '../svg/icon-lucide-bookclub.vue'
import IconUser from '../svg/icon-lucide-user.vue'
// floating ui

// Components
import IconBook from '@/components/svg/icon-book.vue'
import IconFeed from '@/components/svg/icon-feed.vue'
// import searchBar from './navigation/searchBar.vue'
import IconBookshelves from '../svg/icon-bookshelves.vue'
import IconBack from '@/components/svg/icon-back.vue'
import IconClubFeed from '@/components/svg/icon-feed-club.vue'
import IconClubSettings from '@/components/svg/icon-club-settings.vue'
import IconExit from '../svg/icon-exit.vue'
import CommentBar from './bookclubs/club/posts/comments/CommentBar.vue'

// services
import { navRoutes } from '../../services/urls'
import {
  goToSearchPage,
  goToFeedPage,
  goToSocialPage,
  goToUserPage,
  goToBookshelvesPage,
  goToBookClubsPage,
  FooterViews,
} from './footernavService'
import { PubSub } from '../../services/pubsub'

const isSearchBarActive = ref(false)
const minimizeFooter = ref(false)
const commentingForClubPost = ref(false)
const clubPostCommentMetaData = ref({})

const route = useRoute()
const { user } = route.params
const router = useRouter()

// instantiate a footer nav service for when you want to swap out which buttons are shown.
const footerView = computed(() => {
  // Check to see if we want to load the bookclub nav instead
  let bookclub = route.params.bookclub
  if (bookclub) {
    return FooterViews.bookclubs
  }

  return FooterViews.default
})

window.addEventListener('toggleSearchBar', () => {
  isSearchBarActive.value = !isSearchBarActive.value
})

// This lets us know when and what to show on the footer
// in case you are leaving a comment inside of a book club.
PubSub.subscribe('start-commenting-club-post', (commentData) => {
  commentingForClubPost.value = true
  clubPostCommentMetaData.value = commentData
})
</script>
<style scoped>
.hidden {
  display: none !important;
}
/* mobile styles */
nav {
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  min-width: min-content;
  display: flex;
  justify-content: space-around;
  padding: 1rem;
  background: linear-gradient(45deg, rgba(235, 241, 255, 1), rgba(255, 255, 255, 0.8));
  backdrop-filter: blur(5px);
  transition-duration: 250ms;
  transition-timing-function: ease-in-out;
}

nav.minimized {
  display: none !important;
  position: absolute;
  bottom: -100px !important;
  left: 0;
  transition: 250ms;
}

nav .nav-button-group {
  padding: 0;
}

/* Mobile only stuff for create menu */
@media screen and (max-width: 768px) {
  .detach-on-mobile {
    position: relative;
  }

  .detach-trigger {
    width: min-content;
  }

  .detach-on-mobile .detached-content[data-state='open'] {
    position: absolute;
    bottom: 40px;
    left: 10px;
    z-index: 99999;
    background-color: var(--surface-primary);
    width: 150px;
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-md);
    border: 1px solid var(--stone-200);
    transition-duration: 0ms;
  }

  .nav-menu-option button {
    display: grid;
    grid-template-columns: 1;
    justify-items: center;
    align-items: center;
    gap: 0.15rem;
    cursor: pointer;
    color: #5a67d8;
    font-weight: 500;
    padding: 0.4rem 0.25rem;
    border-radius: 0.5rem;
  }
}

.show-footer-nav {
  position: fixed;
  padding: 14px 24px;
  width: 80px;
  background-color: var(--indigo-300);
  border-radius: var(--radius-sm);
  bottom: 10px;
  left: 50%;
  transform: translate(-50%, 0);
  opacity: 0.95;
  transition-duration: 250ms;
}

.show-footer-nav:hover {
  background-color: var(--indigo-200);
  cursor: pointer;
  width: 100px;
}

.show-footer-nav .message {
  position: absolute;
  bottom: 30px;
  left: 50%;
  width: 80px;
  transform: translateX(-50%);
  text-align: center;
  white-space: nowrap;
  font-size: var(--font-lg);
  font-family: var(--fancy-script);
  color: var(--indigo-500);
}

.nav-button-group p {
  font-size: var(--font-xs);
}

@media only screen and (min-width: 768px) {
  nav {
    position: fixed;
    top: 5vh;
    width: min-content;
    max-width: 200px;
    height: calc(100% - 100px);
    height: fit-content;
    display: flex;
    flex-direction: column;
    justify-content: start;
    row-gap: 0.65rem;
    align-items: start;
    background: linear-gradient(45deg, rgba(235, 241, 255, 0.5), rgba(255, 255, 255, 0));
    backdrop-filter: blur(5px);
    margin-left: 1ch;
    border-radius: 0.75rem;
    margin-top: 10rem;
  }

  nav.minimized {
    max-width: 3ch;
    transition-duration: 250ms;
    transition-timing-function: ease-in-out;
  }

  .hidden-on-mobile {
    display: block !important;
  }

  .nav-button-group {
    position: sticky;
    top: 3rem;
    display: flex;
    justify-content: start;
    border-radius: 0.5rem;
    width: 100%;
  }

  .nav-button-group svg {
    height: 20px;
    width: 20px;
  }

  /* #Todo: Make the search bar responsive so it looks better on mobile and desktop */
  .searchbar {
    display: flex;
    flex-direction: column;
    flex-basis: 1;
    justify-content: space-around;
  }
}

.footer-nav-button {
  display: flex;
  padding: 6px 8px;
  margin-left: 0.5rem;
  border-radius: 4px;
  /* margin-right: 1ch; */
  color: #667eea;
  align-content: center;
  justify-content: center;
  transition-duration: all 250ms ease;
  text-align: center;
  gap: 4px;

  & svg {
    width: 20px;
    height: 20px;
    margin-left: auto;
    margin-right: auto;
  }

  span {
    align-self: end;
  }
}

.footer-nav-button:hover {
  color: #343fa9;
  background-color: var(--stone-100);
}

.desktop-footer {
  position: fixed;
  left: 0;
  top: 0;
  height: 100%;
}

/* The wrapper */
.club-comment-footer {
  display: flex;
  flex-direction: column;
  row-gap: 8px;
}
</style>
