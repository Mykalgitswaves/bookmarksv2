<template>
  <form class="w-100 max-w-[700px] mx-4 grid grid-cols-1 gap-2 mt-10" action="submitForm" method="POST">
    <label class="text-gray-600 text-sm" for="searchForBooks">
      Search for a book and tap to add it to your books
    </label>

    <input
      class="w-100 grid col-span-1 py-2 px-4 rounded-md border-2 border-indigo-300 border-solid"
      @change="searchBooks($event)"
      placeholder="Search for books"
      name="searchForBooks"
      type="text"
    />
  </form>

  <form class="mx-4 w-100 max-w-[700px] grid grid-cols-5 place-content-center gap-5 mt-5">
    <span class="grid col-span-5 gap-2">
      <label class="block" for="initial-thoughts">Your thoughts on this book</label>
      <textarea
        class="block border-2 border-solid border-indigo-300 rounded-md px-4 py-2"
        width="100"
        name="initial-thoughts"
        rows="4"
      />
    </span>

    <span class="grid col-span-5 gap-2">
      <label class="block" for="initial-thoughts"
        >How would you describe this book to a friend</label
      >
      <textarea
        type="text"
        width="100"
        class="w-100 border-2 border-solid border-indigo-300 rounded-md px-4 py-2"
      />
    </span>

    <span class="grid">
      <label class="whitespace-nowrap" for="">How would you rate this book</label>

      <span class="flex flex-row gap-2">
        <button
          class="text-indigo-500 rounded-md"
          v-for="(rating, index) in ratings"
          :key="index"
        >
          <Star class="text-indigo-500" />
        </button>
      </span>
    </span>
  </form>

  <button
    class="block h-4 mx-4 mt-10 bg-indigo-600 text-indigo-100 px-6 py-3 rounded-md hover:bg-indigo-700 duration-300"
  >
    Post review
  </button>
</template>

<script>
import Star from '../../svg/icon-star.vue'
export default {
  components: {
    Star
  },
  props: {
    ratings: {
      type: Array,
      required: true
    }
  }
}
</script>
