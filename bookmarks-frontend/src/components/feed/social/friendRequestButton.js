import { db } from '../../../services/db';
import { urls } from '../../../services/urls';
import IconCheck from '../../svg/icon-check.vue';
import IconExit from '../../svg/icon-exit.vue';

export const friendRequestButtons = {
    'anonymous': [
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