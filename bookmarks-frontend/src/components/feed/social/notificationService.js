
import { db } from '../../../services/db';
import { urls } from '../../../services/urls';

// TODO: define endpoint calls for various activity types.

export function acceptFriendRequest(anonUserId, callbackFunction) {
    db.put(urls.user.acceptAnonFriendRequest(anonUserId), null, false, 
        (res) => {
            if (callbackFunction) {
                callbackFunction(res)
            }
        }, 
        (err) => {
            console.error(err);
        }
    );
}

export function declineFriendRequest(anonUserId, callbackFunction) {
    db.put(urls.user.declineAnonFriendRequest(anonUserId), null, false, 
        (res) => {
            if (callbackFunction) {
                callbackFunction(res)
            }
        }, 
        (err) => {
            console.error(err);
        }   
    )
}