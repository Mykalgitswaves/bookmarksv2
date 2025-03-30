import { ref } from "vue";
import { defineStore } from 'pinia';
import { urls } from "@/services/urls";
import { db } from "@/services/db";

interface CurrentUserProps {
    id: String;
    email: String;
    created_date: String;
    username: String;
    full_name?: String;
    bio?: String;
    // Property that represents a users relationship to a given club they are viewing. 
    clubs: {
        [key: string]: Object;
    };
};

// Used to globally access the current user.
export const currentUser = ref<CurrentUserProps>({
    id: '',
    email: '',
    created_date: '',
    username: '',
    clubs: {}
});

// Maybe get rid of this shit at somepoint.
export const useCurrentUserStore = defineStore('currentUser', {
    state: () => ({
      user: {
        id: '',
        email: '',
        created_date: '',
        username: '',
        clubs: {}
      } as CurrentUserProps,
    }),
    actions: {
        async getCurrentUser(userId: String) {
            db.get(urls.user.getUser(userId as string), null, false, (res:any) => {
                    Object.assign(this.user, res.data);
                    console.log(this.user)
                }, (res: any) => {
                    console.log(res);
                })
        },
        async getCurrentClubRelationshipsOnUser(userId:string,  clubId: string) {
            if (!this.user.id) {
                await this.getCurrentUser(userId);
                console.log(this.user, 'pre club request')
            }

            // If you haven't had the current club saved, create a new dict for one with the key being the club id
            if (!this.user.clubs[clubId]) {
                this.user.clubs[clubId] = {};
            }

            await db.get(
                urls.bookclubs.getCurrentlyReadingStatusForClub(clubId), 
                null, 
                false, 
                (res) => { 
                    this.user.clubs[clubId] = {
                        userFinishedWithCurrentBook: res.data.is_user_finished_with_current_book,
                        clubFinishedWithCurrentBook: res.data.is_club_finished_with_current_book,
                        isOwner: res.data.is_owner,
                        isMember: res.data.is_member,
                    }
                }, (err) => {
                    console.log(err);
                }
            );
            console.log(this.user, 'post club request')
        },
    },
});

// The function used to actually get the current user.
export async function getCurrentUser(userId: String) {
    db.get(urls.user.getUser(userId as string), null, false, (res:any) => {
        currentUser.value = res.data;
    }, (res: any) => {
        console.log(res);
    });
};

export async function setCurrentClubRelationshipsOnUser(clubId: string, currentUserRef:any) {
    // If you haven't had the current club saved, create a new dict for one
    if (!currentUserRef && !currentUserRef.clubs) {
        currentUserRef.clubs = {};
        currentUserRef.clubs[clubId] = {};
    }

    await db.get(
        urls.bookclubs.getCurrentlyReadingStatusForClub(clubId), 
        null, 
        false, 
        (res) => { 
            currentUserRef.clubs[clubId] = {
                user: res.data.is_user_finished_with_current_book,
                club: res.data.is_club_finished_with_current_book,
                isOwner: res.data.is_owner,
                isMember: res.data.is_member,
            }
        }, (err) => {
            console.log(err);
        }
    );
    console.log(currentUserRef);

    Object.assign(currentUser.value, {clubs: currentUserRef.clubs});
}