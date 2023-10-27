<template>
  <div class="h-100 grid place-content-center relative mt-10">
    
    <div id="subnavcreate" class="flex flex-row gap-5 w-100 justify-center mt-10 mb-20">
      <button type="button" @click="getPrevPage">Prev</button>
      <p class="text-indigo-500 mx-2">
        <span class="text-indigo-800 underline underline-offset-2">{{ page + 1 }}</span> / 5
      </p>
      <button type="button" @click="getNextPage">Next</button>
    </div>
    
    <teleport to="body">
          <MobileMenu/>
    </teleport>

    <component :is="createFormState" />
  </div>
</template>

<script>
// Import create user form components
import CreateUser from '@/components/create/createuserstart.vue';
import CreateUserName from '@/components/create/createusername.vue';
import CreateUserFormBooks from '@/components/create/createuserformbooks.vue';
import CreateUserFormGenre from '@/components/create/createusergenre.vue';
import CreateUserFormFinal from '@/components/create/createuserfinal.vue';
import NavIcon from '@/components/svg/icon-menu.vue';
import PlaceholderIcon from '@/components/svg/icon-placeholder.vue';
import Logo from '@/components/svg/icon-logo.vue'
import MobileMenu from '@/components/create/menu.vue'

import { computed } from 'vue'
import { useStore } from '../stores/page.js'
import { useBookStore } from '../stores/books.js'

// Map to components keep the view the same
const userFormMapping = {
  0: CreateUser,
  1: CreateUserName,
  2: CreateUserFormBooks,
  3: CreateUserFormGenre,
  4: CreateUserFormFinal
}

export default {
  components: {
    NavIcon,
    Logo,
    PlaceholderIcon,
    MobileMenu
  },
  data() {
    return {
      createFormState: null,
      state: null,
      isMenuHidden: true,
      isBookInMenu: {
        type: Boolean,
        default: false
      }
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
    },
    books() {
      const state = useBookStore()
      return state.books
    },
    genres() {
      const state = useBookStore()
      if(state.genres.length === 0) {
        return this.genrePlaceholder
      } else {
        return state.genres
      }
    },
    authors() {
      const state = useBookStore()
      const authors = state.authors
      if(authors.length === 0) {
        return this.authorPlaceholder
      } else {
        return authors
      }
    }
  },
  mounted() {
    const state = useStore()
    this.state = state
    this.createFormState = computed(() => userFormMapping[state.page])
  }
}
</script>
