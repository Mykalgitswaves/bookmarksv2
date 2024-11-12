<template>
  <TopNav/>
  <div class="sidebar">
    <div class="main-layout">  
      <div class="search-results" v-if="hasSearchResults">
        <CloseButton @close="hasSearchResults = false"/>
        <!-- THis one works -->
        
        <!-- This stuff doesnt -->
        <div  class="transition mt-5">
          <div class="search-results-category" v-if="users.length">
            <div v-for="user in users" :key="user.id" class="search-result">
              {{ user.username }}
            </div>
          </div>

          <div class="search-results-category" v-if="books.length">
            <div v-for="book in books" :key="index" class="search-result book">
              <img class="book-img" :src="book.small_img_url" alt="">

              <h4 class="text-center fancy bold pb-5">{{ book.title }}</h4>

              <button class="btn-tiny btn-wide">
                Go to book
              </button>
            </div>
          </div>

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
import LoadingCard from '@/components/shared/LoadingCard.vue';
import { ref } from "vue";
import { useRoute } from 'vue-router';
import { db } from '../services/db'
import { urls } from '../services/urls'
import { PubSub } from '../services/pubsub';

const route = useRoute();

const hasSearchResults = ref(false);

let books = [];
let authors = [];
let users = [];
let booksByAuthor = [];
let booksByGenre = [];

db.authenticate(urls.authUrl, route.params.user);

PubSub.subscribe('nav-search-get-data', (data) => {
  // manually make ui rerender after these lists get dynamically filled up.
  hasSearchResults.value = false;
  // manually fill up these lists;
  books = data.books;
  authors = data.authors;
  users = data.users;
  booksByAuthor = data.books_by_author;
  booksByGenre = data.books_by_genre;

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
  }

  .search-results-category {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    min-height: fit-content;
    align-items: end;
    justify-content: space-around;
  }

  .search-result {
    border: 1px solid var(--stone-200);
    background-color: var(--stone-50);

    &.book {
      .book-img {
        height: 80px;
        border-radius: 2px;
      }
    }
  }
</style>

