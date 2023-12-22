import { db } from '../../../services/db';
import { urls } from '../../../services/urls';
import IconCheck from '../../svg/icon-check.vue';
import IconExit from '../../svg/icon-exit.vue';

// We can use this to match the payloads with the click events below!
// make sure to spread the function like below:
// .click(...currentClickPayload(rel_to_user, curr_user_id, user_id ))
export function currentClickPayload(rel_to_user, curr_user_id, user_id) {
    if(rel_to_user === 'anonymous_user_friend_requested'){
        return [rel_to_user, curr_user_id, user_id];
    }
}

export const friendRequestButtons = {
    'anonymous_user_friend_requested': [
        {
            click: async (rel_to_user, user_id, friend_id) => await db.put(urls.user.acceptAnonFriendRequest(user_id, friend_id)).then((res) => {
                if (res.status === 200) {
                    rel_to_user = 'friends';
                    return rel_to_user
                }
            }),  
            type: 'button',
            alt: 'accept',
            text: 'Accept',
            class: 'friend-request-accept-btn',
            icon: IconCheck
        },
        {
            click: async (user_id, friend_id) => db.put(urls.user.declineAnonFriendRequest(user_id, friend_id)),
            type: 'button',
            alt: 'decline',
            text: 'Decline',
            class: 'friend-request-reject-btn',
            icon: IconExit
        }
    ],
    'friends': [
        {
            type: 'button',
            alt: 'friends',
            text: 'Friends',
            class: 'text-indigo-600 font-italic',
            icon: null
        }
    ]
}

