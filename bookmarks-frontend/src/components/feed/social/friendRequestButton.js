import { db } from '../../../services/db';
import { urls } from '../../../services/urls';

import IconCheck from '../../svg/icon-check.vue';
import IconExit from '../../svg/icon-exit.vue';

// We can use this to match the payloads with the click events below!
// make sure to spread the function like below:
// .click(...currentClickPayload(rel_to_user, curr_user_id, user_id ))
export function currentClickPayload(curr_user_id, user_id) {
    return [curr_user_id, user_id];
}

export const friendRequestButtons = {
    'anonymous_user_friend_requested': [
        {
            click: async (user_id, friend_id) => await db.put(urls.user.acceptAnonFriendRequest(user_id, friend_id)).then((res) => {
                return 'friends';
            }),
            type: 'button',
            alt: 'accept',
            text: '',
            classes: 'friend-request-accept-btn',
            icon: IconCheck
        },
        {
            click: async (user_id, friend_id) => db.put(urls.user.declineAnonFriendRequest(user_id, friend_id)).then((res) => {
                return 'declined';
            }),
            type: 'button',
            alt: 'decline',
            text: '',
            classes: 'friend-request-reject-btn',
            icon: IconExit
        }
    ],
    'declined': [
        {   
            click: () => null,
            type: 'button',
            alt: 'declined',
            text: 'Declined',
            classes: 'friend-request-declined-text',
            icon: null,
        },
        {
            click: async (user_id, anon_id) => db.put(urls.user.blockAnonFriendRequest(user_id, anon_id)).then((res) => {
                return 'blocked'
            }),
            type: 'button',
            alt: 'block',
            text: 'Block',
            classes: 'friend-request-reject-btn block',
            icon: null,
        }
    ],
    'friends': [
        {
            click: () => null,
            type: 'button',
            alt: 'friends',
            text: '',
            classes: 'text-indigo-600 font-italic',
            icon: null
        }
    ]
}

