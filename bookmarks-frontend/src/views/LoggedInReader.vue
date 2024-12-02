<template>
  <TopNav />

  <div class="sidebar">
    <div class="main-layout">  
      <div class="search-results" v-if="hasSearchResults">
        <CloseButton @close="hasSearchResults = false"/>
        <!-- THis one works -->
        
        <!-- This stuff doesnt -->
        <div class="transition mt-5">
          <div class="search-results-category" v-if="users.length">
            <div v-for="user in users" :key="user.id" class="search-result">
              {{ user.username }}
            </div>
          </div>

          <h3 class="fancy text-xl text-stone-700 mb-5">Books: {{ books.length }}</h3>

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

          <h3 class="fancy text-xl text-stone-700 mb-5" v-if="book_clubs.length">Book Clubs: {{ book_clubs.length }}</h3>

          <div class="search-results-category" v-if="book_clubs.length">
            <!-- book loop -->
            <div v-for="book_club in book_clubs" :key="book_club.id" 
              class="search-result book relative"
              @click="() => {
                router.push(navRoutes.toBookClubFeed(route.params.user, book_club.id)); 
                hasSearchResults = false;
              }"
            >
              <img class="book-img" :src="book_club?.current_book?.small_img_url || noBookYetUrl" alt="" />

              <h4 class="text-center fancy bold pb-5 text-sm">{{ book_club.name }}</h4>
              <h4 class="text-center fancy pb-5 text-sm" v-if="book_club.current_book">
                Currently Reading:\s
                <span class="italic">{{ book_club.current_book.title }}</span>
              </h4>
              <h4 class="text-center fancy pb-5 text-sm" v-else>
                  Not reading anything right now...
              </h4>
            </div>
          </div>

          <h3 class="fancy text-xl text-stone-700 mb-5" v-if="authors.length">Authors: {{ authors.length }}</h3>

          <div class="search-results-category" v-if="authors.length">
            <div v-for="author in authors" :key="author.id" class="search-result">
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
let book_clubs = [];
let authors = [];
let users = [];
let booksByAuthor = [];
let booksByGenre = [];

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
  book_clubs = data.book_clubs;

  hasSearchResults.value = true;
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
  }

  .search-results-category {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
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
</style>

