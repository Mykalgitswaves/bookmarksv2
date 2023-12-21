import { db } from '../../../services/db';
import { urls } from '../../../services/urls';
import IconCheck from '../../svg/icon-check.vue';
import IconExit from '../../svg/icon-exit.vue';

// We can use this to match the payloads with the click events below!
// make sure to spread the function like below:
// .click(...currentClickPayload(rel_to_user, curr_user_id, user_id ))
export function currentClickPayload(rel_to_user, curr_user_id, user_id) {
    if(rel_to_user === 'anonymous_user_friend_requested'){
        return [curr_user_id, user_id];
    }
}

export const friendRequestButtons = {
    'anonymous_user_friend_requested': [
        {
            click: async (user_id, friend_id) => db.put(urls.user.sendAnonFriendRequest(user_id, friend_id)),  
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
    ]
}

