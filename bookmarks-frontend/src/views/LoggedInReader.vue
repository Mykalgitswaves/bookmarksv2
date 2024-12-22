<template>
  <AsyncComponent :promises="[authPromise]">
    <template #resolved>
      <TopNav />

      <div class="sidebar">
        <div class="main-layout"> 

          <!-- Search RESULTS BABY -->
          <div class="search-results" 
            v-if="hasSearchResults"
          >
            <CloseButton class="ml-auto" 
              @close="hasSearchResults = false"
            />
          
            <div class="transition mt-5">
              <h3 class="fancy text-xl text-stone-700 my-5" 
                v-if="searchData.books.length"
              >
                Books: {{ searchData.books.length }}
              </h3>

              <div class="search-results-category" 
                v-if="searchData.books.length"
              >
                <!-- book loop -->
                <div v-for="book in searchData.books" :key="book.id" 
                  class="search-result book relative"
                  @click="() => {
                    router.push(navRoutes.toBookPageFromPost(route.params.user, book.id)); 
                    hasSearchResults = false;
                  }"
                >
                  <img class="book-img" :src="book.img_url" alt="" />

                  <h4 class="text-center fancy bold pb-5 text-sm">{{ book.title }}</h4>
                </div>
              </div>

              <h3 class="fancy text-xl text-stone-700 my-5" 
                v-if="searchData.users.length"
              >
                Users: {{ searchData.users.length }}
              </h3>

              <div class="search-results-category" v-if="searchData.users.length">
                <div v-for="user in searchData.users" :key="user.id"
                  class="search-result user"
                  @click="() => {
                    router.push(navRoutes.toUserPage(route.params.user, user.id)); 
                    hasSearchResults = false;
                  }"
                >
                  <h4 class="text-center fancy bold pb-5 text-sm">{{ user.username }}</h4>

                  <button 
                    v-if="relationshipConfig[user.relationship_to_current_user]?.label"
                    :class="relationshipConfig[user.relationship_to_current_user].class"
                    @click="relationshipConfig[user.relationship_to_current_user].action(user)"
                  >
                    {{ relationshipConfig[user.relationship_to_current_user].label }}
                  </button>
                </div>
              </div>

              <h3 class="fancy text-xl text-stone-700 my-5" 
                v-if="searchData.bookClubs.length"
              >
                Book Clubs: {{ searchData.bookClubs.length }}
              </h3>

              <div class="search-results-category" v-if="searchData.bookClubs.length">
                <!-- book loop -->
                <div v-for="bookClub in searchData.bookClubs" :key="bookClub.id" 
                  class="search-result book relative"
                  @click="() => {
                    router.push(navRoutes.toBookClubFeed(route.params.user, bookClub.id)); 
                    hasSearchResults = false;
                  }"
                >
                  <img class="book-img" :src="bookClub?.current_book?.small_img_url || noBookYetUrl" alt="" />

                  <h4 class="text-center fancy bold pb-5 text-sm">{{ bookClub.name }}</h4>
                  <h4 class="text-center fancy pb-5 text-sm" v-if="bookClub.current_book">
                    Currently Reading:&nbsp;
                    <span class="italic">{{ bookClub.current_book.title }}</span>
                  </h4>
                  <h4 class="text-center fancy pb-5 text-sm" v-else>
                      Not reading anything right now...
                  </h4>
                </div>
              </div>

              <h3 class="fancy text-xl text-stone-700 my-5" 
                v-if="searchData.bookshelves.length"
              >
                Bookshelves: {{ searchData.bookshelves.length }}
              </h3>

              <div class="search-results-category" v-if="searchData.bookshelves.length">
                <!-- book loop -->
                <div v-for="bookshelf in searchData.bookshelves" :key="bookshelf.id" 
                  class="search-result book relative"
                  @click="() => {
                    router.push(navRoutes.toBookshelfPage(route.params.user, bookshelf.id)); 
                    hasSearchResults = false;
                  }"
                >
                  <img class="book-img" :src="bookshelf?.first_book?.small_img_url || noBookYetUrl" alt="" />

                  <h4 class="text-center fancy bold pb-5 text-sm">{{ bookshelf.name }}</h4>
      
                  <h4 class="text-center fancy pb-5 text-sm">
                    {{ bookshelf.description }}
                  </h4>
                </div>
              </div>

              <h3 class="fancy text-xl text-stone-700 my-5" 
                v-if="searchData.authors.length"
              >
                Authors: {{ searchData.authors.length }}
              </h3>

              <div class="search-results-category" v-if="searchData.authors.length">
                <div v-for="author in searchData.authors" :key="author.id" class="search-result authors">
                  {{ author.name }}
                </div>
              </div>
            </div>
          </div>

          <!-- IF YOU DONT HAVE SEARCH RESULTS THEN SHOW THE EXPECTED ROUTE -->
          <RouterView v-else></RouterView>
        </div>

        <FooterNav/>
      </div>
    </template>

    <template #loading>
      <div>
        Authenticating....
      </div>
    </template>
  </AsyncComponent>
</template>
<script setup>
import TopNav from '@/components/feed/topnav.vue';
import FooterNav from '@/components/feed/footernav.vue'
import CloseButton from '../components/feed/partials/CloseButton.vue';
import { ref, computed } from "vue";
import { useRoute, useRouter } from 'vue-router';
import { db } from '../services/db'
import { urls, navRoutes } from '../services/urls'
import { PubSub } from '../services/pubsub';
import AsyncComponent from '@/components/feed/partials/AsyncComponent.vue';

const route = useRoute();
const router = useRouter();


const noBookYetUrl = 'https://placehold.co/45X45';

const searchData = ref({
  books: [],
  authors: [],
  users: [],
  books_by_author: [],
  books_by_genre: [],
  bookClubs: [],
  bookshelves: []
});

// This will make ui rerender whenever any dependency changes in length.
const hasSearchResults = computed(() => Object.values(searchData.value).some((val) => val.length));

const authPromise = db.authenticate(urls.authUrl, route.params.user);

PubSub.subscribe('nav-search-get-data', (data) => {
  Object.entries(data).forEach(([key, value]) => {
    // destructure the general search object to get the keys and values from the key and value (IK this sucks)
    // ON^2
      if (key === 'general_search') {
        Object.entries(value).forEach(([key, value]) => {
          searchData.value[key] = value;
        });
      }
      // this is for the other search types
      searchData.value[key] = value;
    });
});

const relationshipConfig = {
      stranger: {
        label: "Add Friend",
        class: "btn btn-tiny text-sm bg-indigo-500 text-white mx-auto",
        action: sendFriendRequest,
        show: true,
      },
      current_user_blocked_by_anonymous_user: {
        label: "Add Friend",
        class: "btn btn-tiny text-sm bg-indigo-500 text-white mx-auto",
        action: sendFriendRequest,
        show: true,
      },
      friend: {
        label: "Friend",
        class: "btn btn-tiny text-sm btn-add-friend text-white mx-auto",
        action: () => {},
        show: true,
      },
      is_current_user: {
        label: "It's you!",
        class: "btn btn-tiny text-sm bg-gray-500 text-white mx-auto",
        action: () => {},
        show: true,
      },
      anonymous_user_blocked_by_current_user: {
        label: "Blocked by you",
        class: "btn btn-tiny text-sm bg-red-500 text-white mx-auto",
        action: () => {},
        show: true,
      },
      anonymous_user_friend_requested: {
        label: "Accept Friend Request",
        class: "btn btn-tiny text-sm bg-yellow-500 text-white mx-auto",
        action: acceptFriendRequest,
        show: true,
      },
      current_user_friend_requested: {
        label: "Pending Friend Request",
        class: "btn btn-tiny text-sm bg-grey-500 text-white mx-auto",
        action: () => {},
        show: true,
      }
    };

function sendFriendRequest(friend) {
  response = db.put(
    urls.user.sendAnonFriendRequest(route.params.user, friend.id), 
    null, 
    false
  ).then((res) => {
    friend.relationship_to_current_user = "current_user_friend_requested";
  }).catch((err) => {
    console.log("Friend request failed", err);
  });
}

function acceptFriendRequest(friend) {
  response = db.put(
    urls.user.acceptAnonFriendRequest(friend.id), 
    null, 
    false
  ).then((res) => {
    friend.relationship_to_current_user = "friend";
  }).catch((err) => {
    console.log("Friend accept failed", err);
  });
}

</script>
<style scoped>
  .main-layout {
    min-height: 100%;
    width: 100%;
    padding: 1.25rem;
    gap: 2ch;
    justify-content: center;
  }

  @media only screen and (min-width: 768px) {
    .main-layout {
      justify-content: start;
      padding-left: 14vw;
    }
    .sidebar {
      display: flex;
      flex-direction: row-reverse;
      justify-content: space-between;
    }
  }

  @media only screen and (min-width: 960px) {
    .main-layout {
      margin-left: 0rem;
    }
  }

  @starting-style {
    .search-results {
      opacity: 0;
    }
  }

  .search-results {
    display: block;
    transition: all 250ms ease;
    border: 1px solid var(--stone-100);
    padding: 12px;
    border-radius: 8px;
    background-color: var(--surface-primary);
    min-height: 400px;
  }

  .search-results-category {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    min-height: fit-content;
    align-items: end;
    justify-content: start;
    column-gap: 10px;
    row-gap: 10px;
  }

  .search-result {
    border: 1px solid var(--stone-200);
    background-color: var(--stone-50);
    padding: 14px;
    transition: all 250ms ease;
    max-width: 300px; /* Set a maximum width */
    margin: 0; /* Ensure it aligns to the left without centering */
    height: 100%;

    &.authors {
      display: grid;
      place-content: center;
      text-align: center;
    }

    &:hover {
      background-color: var(--stone-300);
    }

    &.user {
      display: grid;
      place-content: center;
      text-align: center;
      word-break: break-word;
    }

    &.book {
      height: -webkit-fill-available;

      .book-img {
        height: 100px;
        width: 80px;
        border-radius: 2px;
        padding-bottom: 5px;
        margin-left: auto;
        margin-right: auto;
      }
    }
  }

  .friend-btn {
    font-weight: bold;
    color: var(--indigo-500);
    padding: 1px 8px;
    border: hidden;
    border-radius: 4px;
    background: none; /* No full background */
    cursor: pointer;
  }

  .friend-btn:hover {
    color: var(--indigo-800);
  }

</style>

