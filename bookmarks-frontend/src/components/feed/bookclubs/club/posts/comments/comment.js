import { defineEmits } from "vue";
import { urls } from "../../../../../../services/urls"
import { db } from "../../../../../../services/db"

const emit = defineEmits(['comment-deleted', 'deletion-failed']);

export async function deleteClubComment(comment, bookClubId) {
    db.delete(
        urls.concatQueryParams(
            urls.reviews.deleteComment(comment.id), 
            { bookclub: bookClubId }
        ), null, false, () => {
        emit('comment-deleted', { comment })
    }, () => {
        emit('deletion-failed');
    })
}

export async function likeClubComment(comment, bookClubId) {
    db.put(
        urls.concatQueryParams(
            urls.reviews.likeComment(comment.id), 
            { bookclub: bookClubId }
        ), null, false, () => {
        return true;
    }, () => {
        return false;
    })
}

export async function dislikeClubComment(comment, bookClubId) {
    db.put(urls.concatQueryParams(
        urls.reviews.unlikeComment(comment.id),
        { bookclub: bookClubId }
    ), null, false, (res) => {
        return true;
    }, () => {
        return false;
    })
}