import { urls } from "../../../services/urls";
import { db } from "../../../services/db";

export async function getWantToReadshelfPromise(user_id) {
    const response = await db.get(urls.rtc.getWantToRead(user_id));
    return response;
}