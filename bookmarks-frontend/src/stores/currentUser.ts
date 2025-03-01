import { ref } from "vue";
import { urls } from "@/services/urls";
import { db } from "@/services/db";

interface CurrentUserProps {
    id: String;
    email: String;
    created_date: String;
    username: String;
    full_name?: String;
    bio?: String
};

// used to globally access the current user.
export const currentUser = ref<CurrentUserProps | {}>({});

// The function used to actually get the current user.
export async function getCurrentUser(userId: String) {
    db.get(urls.user.getUser(userId as string), null, false, (res:any) => {
        currentUser.value = res.data;
    }, (res: any) => {
        console.log(res);
    });
};