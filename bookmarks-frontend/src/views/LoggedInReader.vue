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
              @close="() => Object.assign(searchData, SEARCH_DATA_KEYS)"
            />

            <!-- BOOKS -->
            <div class="transition mt-5">
              <div v-if="loadedSearchResults">
                <!-- Are we loading books with an ID? -->
                <div v-if="searchData.books.some((book) => book.id)">
                  <h3 class="fancy text-xl text-stone-700 my-5">
                    Books: {{ searchData.books.length }}
                  </h3>

                  <div class="search-results-category">
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
                </div>
              </div>

              <div v-else class="search-result loading gradient"></div>

              <!-- USERS, make sure you have an ID and they are at least kind of truthy 
              before rendering an empty form on the front end. -->
              <div v-if="loadedSearchResults">
                <div v-if="searchData.users.some((user) => user.id)">
                  <h3 class="fancy text-xl text-stone-700 my-5">
                    Users: {{ searchData.users.length }}
                  </h3>

                  <div class="search-results-category">
                    <div v-for="user in searchData.users" :key="user.id"
                      class="search-result user"
                      :class="{
                        'friends': user.relationship_to_current_user === 'friend',
                        'loading': relationshipConfig[user?.relationship_to_current_user]?.loading,
                        'declined': user.relationship_to_current_user === 'declined',
                      }"
                      @click="() => {
                        router.push(navRoutes.toUserPage(route.params.user, user.id)); 
                        hasSearchResults = false;
                      }"
                    >
                      <h4 class="text-center fancy bold pb-5 text-sm">{{ user.username }}</h4>
                      <div v-if="user.relationship_to_current_user !== 'anonymous_user_friend_requested'">
                        <button 
                          v-if="relationshipConfig[user.relationship_to_current_user]?.label"
                          :class="relationshipConfig[user.relationship_to_current_user].class"
                          @click="relationshipConfig[user.relationship_to_current_user].action(user)"
                        >
                          <span v-if="!relationshipConfig[user.relationship_to_current_user].loading">
                            {{ relationshipConfig[user.relationship_to_current_user].label }}
                          </span>
                          <!-- IF you are waiting for a response from the server then show loading... -->
                          <span v-else>
                            loading...
                          </span>
                        </button>
                      </div>

                      <div v-else class="flex gap-2">
                        <button 
                          type="button" 
                          v-for="(button, index) in relationshipConfig[user.relationship_to_current_user]" 
                          :key="index"
                          :class="button.class"
                          @click="button.action(user)"
                        >
                          {{ button.label }}
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div v-else class="search-result loading gradient"></div>

              <!-- BOOK CLUBS -->
              <div v-if="loadedSearchResults">
                <!-- Check for an id before rendering so we know the object is at least kinda correct. -->
                <div v-if="searchData.bookClubs.some((bookClub) => bookClub.id)">
                  <h3 class="fancy text-xl text-stone-700 my-5">
                    Book Clubs: {{ searchData.bookClubs.length }}
                  </h3>

                  <div class="search-results-category">
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
                </div>
              </div>

              <div v-else class="search-result loading gradient"></div>

              <!-- BOOK SHELVES -->
              <div v-if="loadedSearchResults">
                <div v-if="searchData.bookshelves.some((bookshelf) => bookshelf.id)">
                  <h3 class="fancy text-xl text-stone-700 my-5">
                    Bookshelves: {{ searchData.bookshelves.length }}
                  </h3>

                  <div class="search-results-category">
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
                </div>
              </div>

              <div v-else class="search-result loading gradient"></div>


              <!-- AUTHORS -->
              <div v-if="loadedSearchResults">
                <div v-if="searchData.authors.some((author) => author.id)">
                  <h3 class="fancy text-xl text-stone-700 my-5">
                    Authors: {{ searchData.authors.length }}
                  </h3>

                  <div class="search-results-category" v-if="searchData.authors.length">
                    <div v-for="author in searchData.authors" :key="author.id" class="search-result authors">
                      {{ author.name }}
                    </div>
                  </div>
                </div>
              </div>
              
              <div v-else class="search-result loading gradient"></div>
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
import { ref, computed, watch, nextTick, onMounted } from "vue";
import { useRoute, useRouter } from 'vue-router';
import { db } from '../services/db'
import { urls, navRoutes } from '../services/urls'
import { PubSub } from '../services/pubsub';
import AsyncComponent from '@/components/feed/partials/AsyncComponent.vue';
import { getCurrentUser } from './../stores/currentUser';

const route = useRoute();
const router = useRouter();
const { user } = route.params;
// Fix for a weird bug we sometimes run into from bad navigation.
// If user is ever undefined make us logout.
watch(() => route.params, (newValue) => {
  if (newValue.user === 'undefined') {
    router.push('/');
  }
}, {immediate: true})

const noBookYetUrl = 'https://placehold.co/45X45';

const SEARCH_DATA_KEYS = {
  books: [],
  authors: [],
  users: [],
  books_by_author: [],
  books_by_genre: [],
  bookClubs: [],
  bookshelves: []
}

const searchData = ref({
  ...SEARCH_DATA_KEYS,
});

// This will make ui rerender whenever any dependency changes in length.
const hasSearchResults = computed(() => Object.values(searchData.value).some((val) => val.length));

const authPromise = db.authenticate(urls.authUrl, route.params.user);

onMounted(async () => {
  try {
    getCurrentUser(user);
  } catch(err) {
    console.log(err);
  }
});

const loadedSearchResults = ref(false);

/**
 * @subscriptions
 * @sub {nav-search-get-data} - When search results are returned from the data, we use this to update the ref.
 * @sub {nav-search-get-data-loaded} - tells us that all search promises have been fulfilled.
 */
PubSub.subscribe('nav-search-get-data', (data) => {
  loadedSearchResults.value = false;
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

PubSub.subscribe('nav-search-get-data-loaded', (symbol) => {
  nextTick(() => {
    loadedSearchResults.value = true;
  });
});

/**
 * @END_SUBSCRIPTIONS
 */

const relationshipConfig = ref({
      stranger: {
        label: "Add Friend",
        class: "btn btn-tiny text-xs bg-indigo-500 text-white mx-auto",
        action: sendFriendRequest,
        show: true,
        loading: false,
      },
      current_user_blocked_by_anonymous_user: {
        label: "Add Friend",
        class: "btn btn-tiny text-xs bg-indigo-500 text-white mx-auto",
        action: sendFriendRequest,
        show: true,
        loading: false,
      },
      friend: {
        label: "Friends",
        class: "btn btn-tiny text-xs btn-already-friends mx-auto",
        action: () => {},
        show: true,
        loading: false,
      },
      is_current_user: {
        label: "It's you!",
        class: "btn btn-tiny btn-specter text-xs text-stone-600 fancymx-auto",
        action: () => {},
        show: true,
        loading: false,
      },
      anonymous_user_friend_requested: [
        {
          label: "Accept 😊",
          class: "btn btn-tiny btn-accept-friend-request text-xs text-white mx-auto",
          action: acceptFriendRequest,
          show: true,
          loading: false,
        },
        {
          label: "Decline 🫥",
          class: "btn btn-tiny btn-decline-friend-request text-xs text-white mx-auto",
          action: declineFriendRequest,
          show: true,
          loading: false,
        }
      ],
      current_user_friend_requested: {
        label: "Request pending",
        class: "btn btn-tiny text-xs mx-auto btn-friend-requested",
        action: () => {},
        show: true,
        loading: false,
      },
      declined: {
        label: "Declined ❌",
        class: "btn btn-tiny text-xs mx-auto btn-specter",
        action: () => null,
        show: true,
        loading: false,
      }
    });

function sendFriendRequest(friend) {
  // this is to show loading when the request is sent
  let oldRelationship = friend.relationship_to_current_user;
  relationshipConfig.value[oldRelationship].loading = true

  db.put(
    urls.user.sendAnonFriendRequest(route.params.user, friend.id), 
    null, 
    false,
    () => {
      relationshipConfig.value[oldRelationship].loading = false
      friend.relationship_to_current_user = "current_user_friend_requested";
    },
    (err) => {
      console.log("Friend request failed", err);
    }
  );
}

function acceptFriendRequest(friend) {
  db.put(
    urls.user.acceptAnonFriendRequest(friend.id), 
    null, 
    false,
    () => {
      friend.relationship_to_current_user = "friend";
    },
    (err) => {
      console.log("Friend accept failed", err);
    }
  );
}

function declineFriendRequest(user) {
  db.delete(
    urls.user.declineAnonFriendRequest(user.id), 
    null, 
    false,
    () => {
      user.relationship_to_current_user = "declined";
    }, 
    (err) => {
      console.log("Friend decline failed", err);
    });
}

// Filter out blocked users from the search results
watch(searchData, (newValue) => {
  loadedSearchResults.value = true;
  searchData.value.users = newValue.users.filter((user) => user.relationship_to_current_user !== 'current_user_blocked_by_anonymous_user')
});
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
    max-width: 1000px;
    margin-left: auto;
    margin-right: auto;
  }

  .search-results-category {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    min-height: fit-content;
    align-items: end;
    justify-content: center;
    column-gap: 10px;
    row-gap: 10px;
  }

  @starting-style {
    .search-result {
      opacity: 0;
    }
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

    &.loading {
      /* filter: blur(1px); */
      border: none;
      border-radius: 8px;
      background-color: var(--stone-100);
      height: 100%;
      max-width: unset;
      width: 100%;
      margin-top: 20px;
      margin-bottom: 20px;
      min-height: 100px;
    }

    &:hover {
      background-color: var(--stone-300);
    }

    &.friends {
      border: 1px solid var(--green-500);
      background-color: var(--green-50);
    }


    &.declined {
      border: 1px solid var(--red-500);
      background-color: var(--red-50);
    }

    &.user {
      border-radius: 8px;
      display: grid;
      place-content: center;
      text-align: center;
      word-break: break-word;
      min-height: -webkit-fill-available;
      align-content: space-between;
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

  .btn-already-friends {
    background-color: var(--green-200);
    color: var(--stone-700);
  }

  .btn-friend-requested {
    background-color: var(--stone-500);
    color: var(--stone-50);
  }

  .btn-accept-friend-request {
    background-color: var(--green-500);
    color: var(--surface-primary);
  }
  
  .btn-decline-friend-request {
    background-color: var(--red-500);
    color: var(--surface-primary);
  }
</style>

