<template>
    <div class="container grid grid-cols-1">
        <h2 class="text-3xl font-medium mb-4">What kind of reader<br> are you?</h2>
        <p class="text-gray-500">Search for some of your favorite books</p>

        <form class="grid grid-cols-1 gap-2"
            action="submitForm"
            method="POST"
        >
            <input
                class="py-2 px-4 rounded-md
                border-2 border-indigo-200 mt-20 
                w-62 max-w-[600px]" 
                @change="searchBooks($event)"
                placeholder="Search for books"
                name="searchForBooks"
                type="text"
            />
            
            <label 
                class="text-gray-600 text-sm"
                for="searchForBooks"
            >
                Search for a book and tap to add it to your books
            </label>
        </form>

        <BookSearchResults 
            :data="data"
        />
        <button
            class="mt-5 px-36 py-3 bg-indigo-600
            rounded-md text-indigo-100" 
            type="submit"
            @click="navigate"
        >Continue</button>
    </div>    
</template>

<script>
    import BookSearchResults from './booksearchresults.vue';
    import { useStore } from '../../stores/page.js';



    export default {
        components: {
            BookSearchResults
        }, 
        data() {
            return {
                formBlob: {},
                data: null,
                state: null
            }
        },
        methods: {
            async getBooks(event) {
              await fetch()
                .then(response => response.json())
                .then((data) => {
                    data.filter((d) => { 
                        d.includes(event.target.value) 
                            ? this.data = d
                            : null;
                    })
                })
            },
            navigate(){
                this.state.getNextPage();
                console.log(this.state.page)
            }
        },
        mounted() {
            this.state = useStore();
        }
    }
</script>