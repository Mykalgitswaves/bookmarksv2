<template>
  <div class="rounded-md w-[100%] mx-12 my-3 px-3 py-3 relative">
    <div class="review">
      <img
        class="h-24 min-w-[80px]"
        src="../../../assets/losingmymindreview.png"
        alt="image preview of book"
      />

      <div>
        <p class="flex flex-row text-xl font-semibold text-gray-800 align-center justify-start">
          {{ review.title }}

          <Stars class="ml-2" :stars="review.stars" />
        </p>

        <p class="text-gray-600">
          {{ truncatedDescription }}

          <span
            v-if="!fullDescShown"
            class="text-gray-900 underline cursor-pointer"
            @click="showFullDescription"
            ><br />... read more</span
          >

          <span v-if="fullDescShown">{{ restOfDescription }}</span>
        </p>
      </div>
    </div>

    <div class="review-controls border-t-[1.5px] border-solid border-indigo-100 pt-2">
      <span>
        <p class="inline mx-4 text-gray-500 cursor-pointer font-medium">Like</p>

        <p
          v-if="review.comments"
          @click="showComment = !showComment"
          class="inline mx-4 text-gray-500 cursor-pointer font-medium"
        >
          {{ review.comments.length }} comments
        </p>
      </span>

      <p class="inline text-gray-500 font-medium text-sm">1:23 pm 07/03/2023</p>
    </div>
    <Comments v-if="showComment" :comments="review.comments" />
  </div>
</template>

<script>
import Comments from './comments.vue'
import Stars from './stars.vue'

export default {
  components: {
    Comments,
    Stars
  },
  data() {
    return {
      fullDescShown: false,
      showComment: false
    }
  },
  props: {
    review: {
      title: {
        type: String,
        required: true
      },
      description: {
        type: String
      }
    }
  },
  methods: {
    showFullDescription() {
      this.fullDescShown = true
    }
  },
  computed: {
    truncatedDescription() {
      return this.review.description.slice(0, 150)
    },
    restOfDescription() {
      return this.review.description.slice(150, this.review.description.length)
    }
  }
}
</script>

<style scoped>
.review {
  display: grid;
  grid-template-areas:
    'd b b'
    'a b b';
  grid-gap: 2ch;
  justify-content: center;
  align-items: center;
  max-width: 700px;
}

.review-controls {
  display: flex;
  flex-direction: row;
  width: 100%;
  justify-content: space-between;
  align-items: center;
}
</style>
