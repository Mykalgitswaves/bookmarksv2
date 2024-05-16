import ComparisonPost from './posts/comparisonPost.vue';
import ReviewPost from './posts/reviewPost.vue';
import UpdatePost from './posts/updatePost.vue';

export const feedComponentMapping = {
    'comparison': {
        component: () => ComparisonPost,
        props: (data) => ({
            key: data?.id,
            headlines: data?.book_specific_headlines,
            bookBlobs: data?.compared_books,
            comparisons: data?.responses,
            comparators: data?.comparators,
            createdDate: data?.created_date,
            username: data?.user_username,
            id: data?.id,
            user_id: data?.user_id,
            likes: data?.likes,
            liked_by_current_user: data?.liked_by_current_user,
            num_comments: data?.num_comments,
            deleted: data?.deleted,
        }),
    },
    'review': {
        component: () => ReviewPost,
        props: (data) => ({
            key: data.id,
            book: data?.book,
            responses: data?.responses,
            spoilers: data?.spoilers,
            likes: data?.likes,
            liked_by_current_user: data?.liked_by_current_user,
            questions: data?.questions,
            question_ids: data?.question_ids,
            headline: data?.headline,
            // post id
            id: data?.id,
            num_comments: data?.num_comments,
            // User info
            username: data?.user_username,
            user_id: data?.user_id,
            posted_by_current_user: data?.posted_by_current_user,
            deleted: data?.deleted
        }),
    },
    'update': {
        component: () => UpdatePost,
        props: (data) => ({
            key: data.id,
            // post id
            id: data?.id,
            // Should contain title, book id, small_img_url
            book: data?.book,
            headline: data?.headline,
            response: data?.response,
            spoiler: data?.spoiler,
            quote: data?.quote,
            page: data?.page,
            username: data?.user_username,
            user_id: data?.user_id,
            likes: data?.likes,
            deleted: data?.deleted,
            num_comments: data?.num_comments,
            comments: data?.comments,
            liked_by_current_user: data?.liked_by_current_user,
        }),
    }
}