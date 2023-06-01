<template>
  <div class="h-screen w-screen grid place-content-center relative">
    <button
      class="mb-10 text-indigo-500 hover:text-indigo-800 duration-300"
      @click="getPrevPage"
    >
      back
    </button>
    <component :is="createFormState" />
  </div>
</template>

<script>
// Import create user form components
import CreateUserFormBooks from '@/components/create/createuserformbooks.vue'
import CreateUserFormGenre from '@/components/create/createusergenre.vue'
import CreateUserFormFinal from '@/components/create/createuserfinal.vue'

import { computed } from 'vue'
import { useStore } from '../stores/page.js'

// Map to components keep the view the same
const userFormMapping = {
  1: CreateUserFormBooks,
  2: CreateUserFormGenre,
  3: CreateUserFormFinal
}

export default {
  data() {
    return {
      createFormState: null,
      state: null
    }
  },
  methods: {
    getNextPage() {
      const state = useStore()
      state.getNextPage()
    },
    getPrevPage() {
      const state = useStore()
      state.getPrevPage()
    }
  },
  computed: {
    page() {
      const state = useStore()
      return state.page
    }
  },
  mounted() {
    const state = useStore()
    this.state = state
    this.createFormState = computed(() => userFormMapping[state.page])
  }
}
</script>
