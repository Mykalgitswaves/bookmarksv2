import { defineStore } from 'pinia';

export const useBookStore = defineStore("addBooks", {
    state: () => ({ 
        books: [],
        genres: [],
        authors: []
    }),
    actions: {
        addBook(book) {
            this.books.push(book);
        },
        removeBook(book) {
            const index = this.state.findIndex((b) => b.pk === book.pk);
            if (index !== -1) {
                this.state.splice(index, 1);
            }
        },
        addGenre(genre) {
            if(this.genres.includes(genre) === false) {
                this.genres.push(genre);
            } 
        },
        addAuthor(author) {
            this.authors.push(author)
        }
    }
})