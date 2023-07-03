<template>
    <div class="review-card">
      <div class="review-card-top">
        <img class="review-card-top-img" :src="props.placeholderBookImg" alt=""/> 
        <div class="review-card-top-text"> 
          <p class="text-xl font-medium text-slate-800">Kitchen Confidential</p>
          <p>Written by <span class="text-indigo-600 underline text-medium">Anthony Bourdain</span><br/> published 2004</p>
          <p class="text-slate-600">Genres: Non-fiction, Short stories & Anthologies</p>
        </div>
      </div> 
      <div class="review-card-body">
        <p class="text-lg text-slate-800 font-medium">Summary</p>
        <p class="text-slate-700">Bourdain spares no one's appetite when he told all about what happens behind the kitchen door. Bourdain uses the same "take-no-prisoners" attitude in his deliciously funny and shockingly delectable book, sure to delight gourmand</p>
      </div> 
      <div class="review-card-bottom-toolbar pt-2">
        <button class="text-indigo-600 font-medium text-lg">
          Bookmark
        </button>
        <router-link :to="`/feed/${props.user}/review/${props.card}`">
          <button class="text-indigo-600 font-medium text-lg">
            14 reviews
          </button>
        </router-link>
      </div>
    </div> 
</template>

<script setup>
  import {defineProps, toRef, onMounted} from 'vue' 
  const props = defineProps({
    placeholderBookImg: String,
    card: Number,
    user: {
      type: Number,
      required: false,
    }
  })
  const { placeholderBookImg } = toRef(props)
  
</script>

<style scoped>
.review-card {
  padding: 15px 20px;
  background-color: #F7FAFC;
  border-radius: .25rem;
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