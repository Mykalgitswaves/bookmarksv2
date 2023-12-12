import { db } from '../../../services/db';
import { urls } from '../../../services/urls'; 
import IconPlus from '../../svg/icon-plus.vue';
import IconRemove from '../../svg/icon-remove.vue';
import IconUnfriend from '../../svg/icon-unfriend.vue';
import IconFollow from '../../svg/icon-follow.vue';
import IconLoading from '../../svg/icon-loading.vue';

export const buttonMap = {
    'anonymous': {
        db: (user, user_id, currentOptionRef) => db.put(urls.user.sendAnonFriendRequest(user, user_id), null, true).then(() => {
            currentOptionRef = 'request-pending'
            return currentOptionRef
        }),
        icon: IconPlus,
        text: 'Add friend',
        classes: 'add-friend'
    },
    'request_pending': {
        db: (user, user_id, currentOptionRef) => db.put(urls.user.unsendAnonFriendRequest(user, user_id), null, true).then(() => {
            currentOptionRef = 'anonymous'
            return currentOptionRef
        }),
        icon: IconRemove,
        text: 'Unsend request',
        classes: 'unsend'
    },
    'friends': {
        db: (user, user_id, currentOptionRef) => db.put(urls.user.unfriendFriend(user, user_id), null, true).then(() => {
            currentOptionRef = 'anonymous'
            return currentOptionRef
        }),
        icon: IconUnfriend,
        text: 'Unfriend',
        classes: 'unfriend'
    },
    'follow': {
        db: (user, user_id, currentOptionRef) => db.put(urls.user.followUser(user, user_id), null, true).then(() => {
            currentOptionRef = 'unfollow'
            return currentOptionRef
        }),
        icon: IconFollow,
        text: 'Follow author',
        classes: 'follow'
    },
    'unfollow': {
        db: (user, user_id, currentOptionRef) => db.put(urls.user.unfollowUser(user, user_id), null, true).then(() => {
            currentOptionRef = 'follow'
            return currentOptionRef
        }),
        icon: IconFollow,
        text: 'unfollow author',
        classes: 'unfollow'
    },
    'loading': {
        db: () => undefined,
        icon: IconLoading,
        text: 'Loading',
        classes: 'loading'
    }
}