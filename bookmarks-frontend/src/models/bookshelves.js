import { ws } from "../components/feed/bookshelves/bookshelvesRtc";
import { db } from "../services/db";
import { urls } from "../services/urls";

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

    exitEditingMode(isEditingValue) {
        ws.unsubscribeFromSocketConnection()
        isEditingValue.value = false;
    },

    /**
     * @async
     * @description promise for moving books to a different shelf. 
     * Optional query param str for removing the book from a current shelf. 
     * @param { String } bookshelf_id: the id of the bookshelf to move the book to. 
     * @param { Object[string] } book_object: 
     *  { title: str, author_names: list[str], small_img_url: str, id: str }
     * @param { Array[String] } movedFromUniqueShelfId: may include:
     *  ['want_to_read', 'currently_reading', 'finished_reading'] for flowshelve bookshelves.
     * Otherwise is an optional string we use to remove the current book from the shelf a
     * user is currently moving a book from.
     */
    async moveBookToShelf(bookshelf_id, book_object, movedFromUniqueShelfId) {
        let payload = new Book(book_object.title, book_object.author_names, book_object.small_img_url, book_object.id);

        try {
            let request;
            if (movedFromUniqueShelfId) {
                request = await db.put(urls.rtc.quickAddBook(bookshelf_id), { book: payload}, null, null, movedFromUniqueShelfId);
            } else {
                request = await db.put(urls.rtc.quickAddBook(bookshelf_id), { book: payload});
            }
            const response = await request.json();
            console.log(response);
        } catch (error) {
            console.error(error);
        }
    }
}


/**
 * @param { String } title
 * @param { Array } author_names
 * @param { String } small_img_url
 * @param { String } id
 */
class Book {
    constructor(title, author_names, small_img_url, id) {
        this.title = title;
        this.author_names = author_names;
        this.small_img_url = small_img_url;
        this.id = id;
    }
}