<template>
  <div class="h-100 grid place-content-center relative mt-10">
    
    
    <teleport to="body">
      <div class="fixed top-0 left-0"> 
        <MobileMenu @iisMenuHidden="isMenuHidden" />
      </div>
    </teleport>

    <div id="subnavcreate" class="flex flex-row gap-5 w-100 justify-center mt-10 mb-20">
      <button type="button" @click="getPrevPage">Prev</button>
      <p class="text-indigo-500 mx-2">
        <span class="text-indigo-800 underline underline-offset-2">{{ page + 1 }}</span> / 4
      </p>
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
import NavIcon from '@/components/svg/icon-menu.vue'
import PlaceholderIcon from '@/components/svg/icon-placeholder.vue';
import Logo from '@/components/svg/icon-logo.vue'
import MobileMenu from '@/components/create/menu.vue'

import { computed } from 'vue'
import { useStore } from '../stores/page.js'
import { useBookStore } from '../stores/books.js'

// Map to components keep the view the same
const userFormMapping = {
  0: CreateUser,
  1: CreateUserFormBooks,
  2: CreateUserFormGenre,
  3: CreateUserFormFinal
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
    console.log(this.books)
  }
}
</script>


<style>
.pop-out-element {
  position: fixed;
  top: 0;
  left: 0;
  z-index: 9999; 
}

.bg_opacity {
  background-color: rgba(244, 246, 255, 0.96);
}

.centered {
  align-items: center;
}
</style>