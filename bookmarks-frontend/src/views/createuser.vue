<template>
  <div class="h-100 grid place-content-center relative mt-10">
    
    
    <teleport to="body">  
      <nav class="fixed top-0 left-0 flex flex-row justify-between w-[100%] px-5 pt-5 pop-out-element">
        <router-link to="/">
          <Logo/>
        </router-link>

        <NavIcon v-bind="$attrs" 
          @click="isMenuHidden = !isMenuHidden"
          :books="books.length" 
          class="text-indigo-600 hover:text-indigo-300 duration-300 cursor-pointer" 
        />
      </nav> 

      <div id="mobilemenu" 
        v-if="!isMenuHidden" 
        class="fixed top-0 left-0 h-screen w-screen z-20 grid place-content-center bg_opacity"
      >
        <h2 class="text-2xl font-semibold text-slate-800 text-center">Your bookshelf</h2>
        
        <div class="mt-10  max-w-[700px] w-90">
          <h4 class="text-xl text-indigo-800">Books</h4>
          
          <div class="flex flex-col align-start max-w-[700px] w-100 border-indigo-600 border-solid border-2">
            <ul>
              <li v-for="(book, index) in books" :key="index"
                class="flex flex-row gap-5 py-4 px-4 place-content-start rounded-md my-3 w-[100%]"
              >
                <img class="h-24" :src="book.img_url" />
                <div class="flex flex-col justify-center">
                  <p class="text-xl font-semibold text-gray-800">
                    {{ book.title }}
                  </p>
                  
                  <p v-for="(name, index) in book.author_names" :key="index" class="inline text-sm text-gray-800">
                    {{ name }}
                  </p>
                  <button class="underline underline-offset-2">remove</button>
                </div>
              </li>
            </ul> 
          </div> 
        </div>

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
import Logo from '@/components/svg/icon-logo.vue'

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
    Logo
  },
  data() {
    return {
      createFormState: null,
      state: null,
      isMenuHidden: true
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
  background-color: rgba(224, 231, 255, 0.96);
}
</style>