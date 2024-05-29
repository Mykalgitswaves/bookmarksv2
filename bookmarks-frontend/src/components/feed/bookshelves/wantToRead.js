import { urls } from "../../../services/urls";
import { db } from "../../../services/db";

export async function getWantToReadshelfPromise(bookshelf) {
    const response = await db.get(urls.rtc.bookShelfTest(bookshelf));
    return response;
}