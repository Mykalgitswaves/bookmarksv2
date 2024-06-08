import { urls } from "../../../services/urls";
import { db } from "../../../services/db";
import { toRaw } from 'vue';

export async function getWantToReadshelfPromise(user_id) {
    const response = await db.get(urls.rtc.getWantToRead(user_id));
    return response;
}

export async function addBook(book) {
    
} 