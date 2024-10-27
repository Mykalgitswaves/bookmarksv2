
import { db } from '../../../services/db';
import { urls } from '../../../services/urls';

const successCallbackForRefreshNotifications = (res) => (res.notifications);
const errorCallbackForRefreshNotifications = (err) => console.warn(err);

export function refreshNotifications(user_id) {
    db.get(urls.user.getNotificationCount(user_id), null, false, successCallbackForRefreshNotifications, errorCallbackForRefreshNotifications);
}