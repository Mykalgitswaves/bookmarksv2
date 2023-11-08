const baseUrl = 'http://127.0.0.1:8000/'

export const urls = {
    // Note there is an extra slash after base so dont start paths with slash
    baseUrl: baseUrl,
    setup: {
        name: baseUrl + 'setup-reader/name',
        bookByText: (text) => (`${baseUrl}books/${text}`),
    },
    authUrl: baseUrl + 'api/auth_user/',
    booksByN: baseUrl + 'books/n/',
    login: baseUrl + 'api/login/',
    author: baseUrl + 'api/author/',
    create: {
        searchBook: (text) => (`${baseUrl}api/search/book/${text}`)
    },
    reviews: {
        review: baseUrl + 'api/review/create_review',
        update: baseUrl + 'api/review/create_update',
        comparison: baseUrl + 'api/review/create_comparison',
        createComment: () => (baseUrl + 'api/review/create_comment'),
        // used in feed
        getReviews: (user_id) => (baseUrl +`api/${user_id}/posts`),
        getComparisons: (user_id) => (baseUrl + `api/${user_id}/comparisons`),
        // getting post data including initial comments on click of comment btn
        getPost: (user_id, id) => (baseUrl + `api/${user_id}/posts/${id}/post`),
        likeComparison: (comparison_id, user_id) => (baseUrl + `api/${user_id}/like/comparisons/${comparison_id}`),
        deleteComment: (comment_id) => (baseUrl + `api/review/${comment_id}/delete`),
        likeComment: (comment_id) => (baseUrl + `api/review/${comment_id}/like`),
        unlikeComment: (comment_id) => (baseUrl + `api/review/${comment_id}/remove_like`),
        getComments: (post_id) =>(baseUrl + `api/review/${post_id}/comments`),
        // calling more comments (duh)
        getMoreComments: (comment_id) => (baseUrl + `api/review/comments/${comment_id}/replies`),
    },
    books: {
        // for book page
        getBookPage: (book_id) => (baseUrl + `api/books/${book_id}`)
        
    }
}