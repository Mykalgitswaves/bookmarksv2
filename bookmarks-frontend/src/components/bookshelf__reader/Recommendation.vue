<template>
  <div
    class="border-solid border-[1px] border-indigo-100 w-auto py-6 rounded-sm my-2 flex flex-row justify-between hover:bg-indigo-50"
  >
    <div class="">
      <p class="mx-4 text-lg text-gray-900 font-semibold">The Policeman</p>
      <p class="mx-4 text-gray-600">Philip K. Dick</p>
    </div>
    <div class="grid gap-2">
      <button class="px-3 py-1 mx-4 text-indigo-600 rounded-md text-sm transition-100">
        <span class="font-bold">+</span> Add
      </button>
      <button class="px-3 py-1 mx-4 text-indigo-600 rounded-md text-sm text-link transition-100">
        <span class="font-bold">-</span> Not interested
      </button>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {}
  },
  methods: {
    addToShelf() {}
  }
}
</script>
