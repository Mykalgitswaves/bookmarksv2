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
    
    <div 
        v-if="!isMenuHidden"
        id="mobilemenu" 
        class="fixed top-0 left-0 h-screen w-screen z-20 grid place-content-center-top bg_opacity gap-5 mt-20"
    >
        <div>
            <div class="text-center mt-10">
                <h2 class="text-2xl font-semibold text-slate-800">Your profile</h2>
                <p class="text-slate-600">An overview of your favorites</p>
            </div>
            <div class="mt-10 grid-3">
                <button 
                    :class="'px-3 py-2 grid-item ' + isSelected('books')"
                    type="button"
                    @click="selected = 'books'"
                >
                    Books
                </button>

                <button 
                    :class="'px-3 py-2 grid-item ' + isSelected('genres')"
                    type="button"
                    @click="selected = 'genres'"
                >
                    Genres
                </button>

                <button 
                    :class="'px-3 py-2 grid-item ' + isSelected('authors')"
                    type="button"
                    @click="selected = 'authors'"
                >
                    Authors
                </button>
            </div>

            <component :is="isSelectedMapping"/>
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

    import authorsList from './menu/AuthorsList.vue';
    import genresList from './menu/GenresList.vue';
    import writersList from './menu/WritersList.vue';


    const componentMap = {
        'books': genresList,
        'genres': authorsList,
        'writers': writersList,
    }

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
                dataBooks: null,
                selected: 'books',
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
            },
            isSelectedMapping()  {
                return componentMap[this.selected]
            }
        },
        methods: {
            emitMenuToggle(){
                this.$emits("isMenuHidden")
            },
            removeBook(book){
                const state = useBookStore();
                this.dataBooks = state.removeBook(book)
            },
            isSelected(option) {
                if (this.selected === option) {
                    return 'active'
                }
            },
        },
        mounted(){
            let state = useBookStore()
            this.dataBooks = state.getBooks();
        }
}
</script>


<style>

.grid-3 {
    display: grid;
    grid-template-columns: repeat(3, 100px);
    justify-content: center;
    gap: 1rem;
}

.grid-item {
    border-bottom: solid 3px rgb(160, 157, 234);
    color: rgb(160, 157, 234);
}

.grid-item.active {
    border-color: rgb(79 70 229);
    color: rgb(79 70 229);
}

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