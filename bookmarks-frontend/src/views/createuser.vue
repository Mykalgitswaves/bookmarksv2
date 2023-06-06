<template>
  <div class="h-100 grid place-content-center relative mt-10">
    <div class="flex flex-row gap-5 w-100 justify-center my-5">
      <button type="button" @click="getPrevPage">Prev</button>
      <p 
        class="text-indigo-500 mx-2" 
      ><span class="text-indigo-800 underline underline-offset-2">{{ page + 1}}</span> / 4</p>
      <button type="button" @click="getNextPage">Next</button>
    </div> 
    <component :is="createFormState" />
  </div>
</template>

<script>
// Import create user form components
import CreateUser from '@/components/create/createuserstart.vue'
import CreateUserFormBooks from '@/components/create/createuserformbooks.vue'
import CreateUserFormGenre from '@/components/create/createusergenre.vue'
import CreateUserFormFinal from '@/components/create/createuserfinal.vue'


import { computed } from 'vue'
import { useStore } from '../stores/page.js'

// Map to components keep the view the same
const userFormMapping = {
  0: CreateUser,
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
