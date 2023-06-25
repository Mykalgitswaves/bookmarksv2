<template>
    <nav class="px-5 pt-5 pop-out-element">
          <router-link to="/">
              <Logo/>
          </router-link>

          <NavIcon v-bind="$attrs" 
              @click="isMenuHidden = !isMenuHidden"
              :books="isBookInMenu === false ? 0 : books.length" 
              class="text-indigo-600 hover:text-indigo-300 duration-300 cursor-pointer" 
          />
    </nav>
    <div id="mobilemenu" 
        class="fixed top-0 left-0 h-screen w-screen z-20 grid place-content-center bg_opacity gap-5"
        v-if="!isMenuHidden"
    >
        <h2 class="mt-20 text-2xl font-semibold text-slate-800 text-center">Your favorite</h2>

        <div class="max-w-[700px] w-90">
            <h4 class="px-5 text-xl text-slate-700">Books</h4>
            
            <div class="flex flex-col align-start max-w-[700px] w-100 ">
           
                <ul>
                    <li v-for="(book, index) in books" :key="index"
                    class="flex flex-row gap-5 px-4 place-content-start rounded-md my-3 w-[100%] min-w-[280px]"
                    >
                        <div class="flex flex-col justify- align-start">
                            <p class="font-semibold text-gray-800">
                            {{ book.title }}
                            </p>
                            
                            <p v-for="(name, index) in book.author_names" :key="index" class="inline text-sm text-gray-800">
                            {{ name }}
                            </p>
                            <button 
                            
                            class="underline underline-offset-2"
                            v-if="isBookInMenu"
                            @click="removeBook(book)"
                            >remove</button>
                        </div>
                    </li>
                </ul> 
       
            </div> 
        </div>
        <div class="px-5">
            <h4 class="text-xl text-slate-700 mb-5">Genres</h4>
            <ul :class="genres.length > 1 ? 'genre-pills' : ''">
                <li v-for="genre in genres" :key="genre.id" class="">
                    <p class="text-gray-800">{{ genre.name }}</p>
                </li>
            </ul>
        </div>

        <div class="w-90 px-5">
            <h4 class="text-xl text-slate-700 mb-5">Authors</h4>
            <ul>
            <li v-for="author in authors" :key="author" class="flex flex-row centered gap-5">
                <p class="text-gray-800">{{ author.name }}</p>
            </li>
            </ul>
        </div>
    </div>
</template>

<script>
    import {toRaw} from "vue" 
    import Logo from '@/components/svg/icon-logo.vue' 
    import NavIcon from '@/components/svg/icon-menu.vue' 
    import { useBookStore } from '@/stores/books.js'

    import placeholder from '@/assets/books.png';
    import genrePlaceholder from '@/assets/literary.png';
    import authorPlaceholder from '@/assets/people.png';

    export default {
        components: {
            NavIcon,
            Logo
        },
        props: {
            
        },
        data(){
            return {
                isMenuHidden: {
                    type: Boolean,
                },
                isBookInMenu: {
                    type: Boolean,
                    default: false
                },
                booksPlaceholder: [{
                    img_url: placeholder,
                    title: 'Good things come to those who look',
                    author_names: [
                        'Search for books and add them to your profile\'s favorites'
                    ]
                }],
                genrePlaceholder: [{
                    img_url: genrePlaceholder,
                    name: 'None added'
                }],
                authorPlaceholder: [{
                    img_url: authorPlaceholder,
                    full_name: 'Anyone come to mind?'
                }],
                dataBooks: null
            }
        },
        computed: {
            books() {
                return this.dataBooks === null ? 0 : this.dataBooks
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
                const authors = state.getAuthors()
                if(authors.length === 0) {
                    return this.authorPlaceholder
                } else {
                    return authors
                }
            }
        },
        methods: {
            emitMenuToggle(){
                this.$emits("isMenuHidden")
            },
            removeBook(book){
                const state = useBookStore();
                this.dataBooks = state.removeBook(book)
            }
        },
        mounted(){
            let state = useBookStore()
            this.dataBooks = state.getBooks();
        }
}
</script>


<style>
.pop-out-element {
  position: fixed;
  top: 0;
  left: 0;
  z-index: 5; 
  display: flex;
  width: 30vw;
  flex-direction: row;
  justify-content: start;
  align-items: center;
  gap: 2ch;
}

.bg_opacity {
  background-color: rgba(244, 246, 255, 0.96);
}

.centered {
  align-items: center;
}
</style>