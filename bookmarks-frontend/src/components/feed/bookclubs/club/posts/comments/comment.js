import { defineEmits } from "vue";
import { urls } from "../../../../../../services/urls"
import { db } from "../../../../../../services/db"

const emit = defineEmits(['comment-deleted', 'deletion-failed']);

export async function deleteComment(comment) {
    db.delete(urls.reviews.deleteComment(comment.id), null, false, () => {
        emit('comment-deleted', { comment })
    }, () => {
        emit('deletion-failed');
    })
}

export async function likeComment(comment) {
    db.put(urls.reviews.likeComment(comment.id), null, false, () => {
        return true;
    }, () => {
        return false;
    })
}