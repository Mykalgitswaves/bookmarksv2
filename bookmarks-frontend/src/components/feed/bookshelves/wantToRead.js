import { urls } from "../../../services/urls";
import { db } from "../../../services/db";
import { toRaw } from 'vue';

export async function getWantToReadshelfPromise(user_id) {
    const response = await db.get(urls.rtc.getWantToRead(user_id));
    return response;
}

export async function addBook(book) {
    let result;
    book = typeof book === 'proxy' ? toRaw(book) : book;
    
    let bookObject = {
        title: book.title,
        id: book.id,
        small_img_url: book.small_img_url,
        author_names: book.author_names,
    };
    
    db.put(
        urls.rtc.quickAddBook('want_to_read'),
        { book: bookObject }
    ).then((res) => {
        result = res.book;
    });

    return result;
} 