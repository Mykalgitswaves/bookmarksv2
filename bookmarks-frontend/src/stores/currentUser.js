import { ref } from "vue";
import { urls } from "../services/urls";
import { db } from "../services/db";

// used to globally access the current user.
export const currentUser = ref({});


// The function used to actually get the current user.
export async function getCurrentUser(userId) {
    db.get(urls.user.getUser(userId), null, false, (res) => {
        currentUser.value = res.data
    }, (res) => {
        console.log(res);
    });
}