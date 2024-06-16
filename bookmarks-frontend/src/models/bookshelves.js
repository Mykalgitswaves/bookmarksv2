import { ws } from "../components/feed/bookshelves/bookshelvesRtc";

export const Bookshelves = {
    WANT_TO_READ: {
        prefix: "want_to_read",
        name: "Want to Read",
    },
    CURRENTLY_READING: {
        prefix: "currently_reading",
        name: "Currently Reading",
    },
    FINISHED_READING: {
        prefix: "finished_reading",
        name: "Finished Reading",
    },

    // Used for appending the list of bookshelves to moveable bookshelves.
    formatFlowShelf: (shelf, user_visibility) => {
        return {
            id: shelf.prefix,
            title: shelf.name,
            visibility: user_visibility
        }
    },

    // Used for moving a book to a specific shelf if.
    moveBookToFlowShelf: async (shelf_id, book_object) => {
        await db.put(urls.rtc.quickAddBook(shelf_id), book_object).then((res) => {
            return res;
        });
    },

    async enterEditingMode(bookshelf, isEditingValue) {
        await ws.createNewSocketConnection(bookshelf).then(() => {
            isEditingValue.value = true;
        });
    },
}