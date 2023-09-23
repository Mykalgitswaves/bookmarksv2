<template>
  <div :class="'review-card ' + bookMarkingStyles">
    <div class="review-card-top">
      <img class="review-card-top-img" :src="work.img_url" :alt="work.title + ' preview image'"/> 

      <div class="review-card-top-text"> 
        <button 
          type="button"
          class="text-xl font-medium text-slate-800"
        >
          {{ work.title }}
        </button>

        <p>Written by 
          <span class="text-indigo-600 underline text-medium">
            <button 
              v-if="work.author_names" 
              type="button" 
              @click="toAuthorPage(work.author_names.id)"
            >
              {{ work.author_names.name }}
            </button>
          </span>

          <br/>

          <span v-if="work.publication_year">published {{ work.publication_year }}</span>
        </p>

        <p v-if="work.genres.length" class="text-slate-600">Genres: 
          <span v-for="(g, index) in work.genres" :key="index">{{ g }}</span>
        </p>
      </div>
    </div> 

    <div class="review-card-body">
      <p class="text-lg text-slate-800 font-medium">Summary</p>

      <p class="text-slate-700">{{ work.description }}</p>
    </div> 

    <div class="review-card-bottom-toolbar pt-2">
      <button 
        class="'font-medium text-lg'"
        type="button"
        @click="bookMarkIt()"
      >
        Bookmark
      </button>

      <button
        v-if="work.reviews && work.reviews.length"
        type="button"
        class="text-indigo-600 font-medium text-lg"
        @click="router.replace(workPage)"
      >
        14 reviews
      </button>
    </div>
  </div> 
</template>

<script setup>
  import { defineProps, ref, computed } from 'vue'
  import { useRoute, useRouter } from 'vue-router'; 

  const props = defineProps({
    work: {
      type: Object,
      required: true,
    },
      user: {
        type: Number,
        required: false,
      }
  })

  const route = useRoute();
  const router = useRouter()
  const workPage = `/feed/${route.params.user}/works/${props.work.id}`;
  const isBookmarking = ref(false);


  const bookMarkingStyles = computed(() => (isBookmarking.value ? 'bg-indigo-500' : ''))

  function toAuthorPage(id) {
    return router.push(`/feed/${route.params.user}/authors/${id}`)
  }

  function bookMarkIt() {
    isBookmarking.value = !isBookmarking.value;
  }
</script>

<style>

.review-card {
  padding: 15px 20px;
  border-radius: .25rem;
  margin-inline: auto;
  min-width: 100%;
  background: var(--background-container-gradient);
}

.review-card-top {
  display: grid;
  grid-template-columns: repeat(2, minmax(min-content, max-content));
  gap: 1.25rem;
}

.review-card-top-img {
  width: 100px;
}

.review-card-top-text {
  display: grid;
  grid-template-columns: 1;
  align-content: space-between;
  height: 100%;
}

.review-card-body {
  padding-top: .5rem;
  padding-bottom: .5rem;
}

.review-card-bottom-toolbar {
  border-top: solid 2px #EDF2F7;
  display: flex;
  flex-direction: row;
  justify-content: space-between;
}
</style>