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


export class CommentService {
    /**
     * Process comments to add depth information
     * @param {Array} comments - Array of comment objects
     * @returns {Array} - Processed comments with depth information
     */
    static processComments(comments) {
        if (!comments || !Array.isArray(comments)) {
            return [];
        }

        /**
         * Recursively process a comment and its replies
         * @param {Object} comment - Comment object
         * @param {number} depth - Current depth level
         * @returns {Object} - Processed comment with depth
         */
        const processComment = (comment, depth = 0) => {
            if (!comment) return null;

            // Create a new object with all the original properties plus depth
            const processedComment = {
                ...comment,
                depth,
                // Ensure replies is always an array
                replies: Array.isArray(comment.replies) ? comment.replies : []
            };

            // Recursively process replies with incremented depth
            if (processedComment.replies.length > 0) {
                processedComment.replies = processedComment.replies.map(reply => 
                    processComment(reply, depth + 1)
                ).filter(Boolean); // Remove any null replies
            }

            return processedComment;
        };

        // Process each top-level comment
        return comments.map(comment => processComment(comment)).filter(Boolean);
    }

    /**
     * Flatten nested comments into a single array with depth information
     * Useful for rendering in a flat list while maintaining depth info
     * @param {Array} comments - Array of comment objects
     * @returns {Array} - Flattened array of comments
     */
    static flattenComments(comments) {
        if (!comments || !Array.isArray(comments)) {
            return [];
        }

        const flattened = [];

        /**
         * Recursively flatten comments and their replies
         * @param {Object} comment - Comment object
         * @param {number} depth - Current depth level
         */
        const flatten = (comment, depth = 0) => {
            if (!comment) return;

            // Add the current comment with its depth
            flattened.push({
                ...comment,
                depth,
                hasReplies: comment.replies && comment.replies.length > 0
            });

            // Recursively flatten replies
            if (comment.replies && comment.replies.length > 0) {
                comment.replies.forEach(reply => flatten(reply, depth + 1));
            }
        };

        // Process each top-level comment
        comments.forEach(comment => flatten(comment));

        return flattened;
    }

    /**
     * Get the maximum depth of the comment tree
     * @param {Array} comments - Array of comment objects
     * @returns {number} - Maximum depth
     */
    static getMaxDepth(comments) {
        if (!comments || !Array.isArray(comments)) {
            return 0;
        }

        const getDepth = (comment) => {
            if (!comment || !comment.replies || !comment.replies.length) {
                return 0;
            }

            return 1 + Math.max(...comment.replies.map(reply => getDepth(reply)));
        };

        return Math.max(...comments.map(comment => getDepth(comment)));
    }

    /**
     * Example usage in a component:
     * 
     * const comments = ref([])
     * const processedComments = computed(() => {
     *     return CommentService.processComments(comments.value)
     * })
     * 
     * // Or if you need a flat list:
     * const flatComments = computed(() => {
     *     return CommentService.flattenComments(comments.value)
     * })
     * 
     * // Get max depth for styling purposes:
     * const maxDepth = computed(() => {
     *     return CommentService.getMaxDepth(comments.value)
     * })
     */
}
