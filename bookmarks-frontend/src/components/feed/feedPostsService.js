import ComparisonPost from './posts/comparisonPost.vue';
import ReviewPost from './posts/reviewPost.vue';
import UpdatePost from './posts/updatePost.vue';

export const feedComponentMapping = {
    'comparison': {
        component: () => ComparisonPost,
        props: (data) => ({
            key: data.id,
            headlines: data.book_specific_headlines,
            bookBlobs: data.compared_books,
            comparisons: data.responses,
            comparators: data.comparators,
            createdDate: data.created_date,
            username: data.user_username,
            id: data.id,
            user_id: data.user_id,
            likes: data.likes,
        })
    },
    'review': {
        component: () => ReviewPost,
        props: (data) => ({
            key: data.id,
            book: data.book,
            title: data.book_title,
            responses: data.responses,
            questions: data.questions,
            spoilers: data.spoilers,
            username: data.user_username,
            likes: data.likes,
            question_ids: data.question_ids,
            headline: data.headline,
            id: data.id,
            small_img_url: data.book_small_img,
            liked_by_current_user: data.liked_by_current_user,
            num_comments: data.num_comments,
            user_id: data.user_id,
        })
    },
    'update': {
        component: () => UpdatePost,
        props: (data) => ({
            key: data.id,
            id: data.id,
            book: data.book,
            title: data.title,
            headline: data.headline,
            response: data.response,
            spoiler: data.spoiler,
            username: data.user_username,
            small_img_url: data.book_small_img,
            page: data.page,
            user_id: data.user_id,
            likes: data.like,
        })
    }
}