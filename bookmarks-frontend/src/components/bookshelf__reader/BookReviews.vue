<template>
  <div
    class="mb-10 md:mt-20 col-span-2 md:col-span-1 col-start-1 col-end-1 border-solid border-b-2 border-indigo-100"
  >
    <div
      class="flex justify-center md:justify-end"
      v-for="(review, index) in pageItems"
      :key="index"
    >
      <Review :review="review" />
    </div>
    <Pagination :pages="pages" @selected-page="handlePageSelection" />
  </div>
</template>

<script>
import Review from './reviews/review.vue'
import Pagination from '../pagination.vue'

export default {
  components: {
    Review,
    Pagination
  },
  props: {
    reviews: {
      type: Array,
      required: false
    }
  },
  data() {
    return {
      itemsPerPage: 3,
      pageItems: []
    }
  },
  methods: {
    handlePageSelection(page) {
      let startIndex = this.itemsPerPage * (page - 1)
      this.pageItems = this.reviews.slice(startIndex, startIndex + this.itemsPerPage)
    }
  },
  computed: {
    pages() {
      return Math.ceil(this.reviews.length / this.itemsPerPage)
    }
  },
  mounted() {
    this.handlePageSelection(1)
  }
}
</script>
