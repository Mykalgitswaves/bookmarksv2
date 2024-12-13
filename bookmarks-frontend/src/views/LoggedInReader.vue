<template>
  <TopNav />

  <div class="sidebar">
    <div class="main-layout">  
      <div class="search-results" v-if="hasSearchResults">
        <CloseButton @close="hasSearchResults = false"/>
        <!-- THis one works -->
        
        <!-- This stuff doesnt -->
        <div class="transition mt-5">
          <h3 class="fancy text-xl text-stone-700 my-5" v-if="books.length">Books: {{ books.length }}</h3>

          <div class="search-results-category" v-if="books.length">
            <!-- book loop -->
            <div v-for="book in books" :key="book.id" 
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

          <h3 class="fancy text-xl text-stone-700 my-5" v-if="users.length">Users: {{ users.length }}</h3>

          <div class="search-results-category" v-if="users.length">
            <div v-for="user in users" :key="user.id"
              class="search-result book relative"
              @click="() => {
                router.push(navRoutes.toUserPage(route.params.user, user.id)); 
                hasSearchResults = false;
              }"
            >
              <!-- <img class="book-img" :src="book.img_url" alt="" /> -->

              <h4 class="text-center fancy bold pb-5 text-sm">{{ user }}</h4>

              <!-- Add a button here to send friend request -->
              <button 
                v-if="relationshipConfig[user.relationship_to_current_user]?.label"
                :class="relationshipConfig[user.relationship_to_current_user].class"
                @click.stop="relationshipConfig[user.relationship_to_current_user].action(user.id)">
                {{ relationshipConfig[user.relationship_to_current_user].label }}
              </button>
            </div>
          </div>

          <h3 class="fancy text-xl text-stone-700 my-5" v-if="bookClubs.length">Book Clubs: {{ bookClubs.length }}</h3>

          <div class="search-results-category" v-if="bookClubs.length">
            <!-- book loop -->
            <div v-for="bookClub in bookClubs" :key="bookClub.id" 
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

          <h3 class="fancy text-xl text-stone-700 my-5" v-if="bookshelves.length">Bookshelves: {{ bookshelves.length }}</h3>

          <div class="search-results-category" v-if="bookshelves.length">
            <!-- book loop -->
            <div v-for="bookshelf in bookshelves" :key="bookshelf.id" 
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

          <h3 class="fancy text-xl text-stone-700 my-5" v-if="authors.length">Authors: {{ authors.length }}</h3>

          <div class="search-results-category" v-if="authors.length">
            <div v-for="author in authors" :key="author.id" class="search-result authors">
              {{ author.name }}
            </div>
          </div>
        </div>
      </div>
      
      <RouterView v-else></RouterView>
    </div>

    <FooterNav/>
  </div>
</template>
<script setup>
import TopNav from '@/components/feed/topnav.vue';
import FooterNav from '@/components/feed/footernav.vue'
import CloseButton from '../components/feed/partials/CloseButton.vue';
import { ref } from "vue";
import { useRoute, useRouter } from 'vue-router';
import { db } from '../services/db'
import { urls, navRoutes } from '../services/urls'
import { PubSub } from '../services/pubsub';

const route = useRoute();
const router = useRouter();

const hasSearchResults = ref(false);
const noBookYetUrl = 'https://placehold.co/45X45';
let books = [];
let authors = [];
let users = [];
let booksByAuthor = [];
let booksByGenre = [];
let bookClubs = [];
let bookshelves = [];

db.authenticate(urls.authUrl, route.params.user);

PubSub.subscribe('nav-search-get-data', (data) => {
  // manually make ui rerender after these lists get dynamically filled up.
  hasSearchResults.value = false;
  // manually fill up these lists;
  console.log("search results ", data);
  books = data.books;
  authors = data.authors;
  users = data.users;
  booksByAuthor = data.books_by_author;
  booksByGenre = data.books_by_genre;
  bookClubs = data.bookClubs;
  bookshelves = data.bookshelves;

  hasSearchResults.value = true;
});

const relationshipConfig = {
      stranger: {
        label: "Add Friend",
        class: "btn friend-btn bg-blue-500 text-white",
        action: sendFriendRequest,
        show: true,
      },
      current_user_blocked_by_anonymous_user: {
        label: "Add Friend",
        class: "btn friend-btn bg-blue-500 text-white",
        action: sendFriendRequest,
        show: true,
      },
      friend: {
        label: "Friend",
        class: "btn friend-btn bg-green-500 text-white",
        action: () => {},
        show: true,
      },
      is_current_user: {
        label: "It's you!",
        class: "btn friend-btn bg-gray-500 text-white",
        action: () => {},
        show: true,
      },
      anonymous_user_blocked_by_current_user: {
        label: "Blocked by you",
        class: "btn friend-btn bg-red-500 text-white",
        action: () => {},
        show: true,
      },
      anonymous_user_friend_requested: {
        label: "Accept Friend Request",
        class: "btn friend-btn bg-yellow-500 text-white",
        action: sendFriendRequest,
        show: true,
      },
      current_user_friend_requested: {
        label: "Pending Friend Request",
        class: "btn friend-btn bg-gray-500 text-white",
        action: () => {},
        show: true,
      }
    };

function sendFriendRequest(userId) {
  console.log("Sending friend request to ", userId);
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

