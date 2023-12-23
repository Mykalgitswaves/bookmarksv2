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
    user: {
        getUser: (user_id) => (baseUrl + `api/user/${user_id}/get_user`),
        setUserImgCdnUrl: (user_id) => (baseUrl + `api/user/${user_id}/update_profile_img`),
        getUserAbout: (user_id) => (baseUrl + `api/user/${user_id}/user_about`),
        updateUsername: (user_id) => (baseUrl + `api/user/${user_id}/update_username`),
        updateBio: (user_id) => (baseUrl +  `api/user/${user_id}/update_bio`),
        updateEmail: (user_id) => (baseUrl + `api/user/${user_id}/update_email`),
        sendAnonFriendRequest: (user_id, friend_id) => (baseUrl + `api/user/${user_id}/send_friend_request/${friend_id}`),
        acceptAnonFriendRequest: (user_id, friend_id) => (baseUrl + `api/user/${user_id}/accept_friend_request/${friend_id}`),
        unsendAnonFriendRequest: (user_id, friend_id) => (baseUrl + `api/user/${user_id}/unsend_friend_request/${friend_id}`),
        declineAnonFriendRequest: (user_id, friend_id) => (baseUrl + `api/user/${user_id}/decline_friend_request/${friend_id}`),
        blockAnonFriendRequest: (user_id) => (baseUrl + `api/user/${user_id}/block`),
        unfriendFriend: (user_id, friend_id) => (baseUrl + `api/user/${user_id}/remove_friend/${friend_id}`),
        followUser: (user_id, friend_id) => (baseUrl + `api/user/${user_id}/follow/${friend_id}`),
        unfollowUser: (user_id, friend_id) => (baseUrl + `api/user/${user_id}/unfollow/${friend_id}`),
        getUsersFriendRequests: (user_id) => (baseUrl + `api/user/${user_id}/friend_requests`)
    },
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
        likePost: (post_id) => (baseUrl + `api/review/${post_id}/like`),
        unlikePost: (post_id) => (baseUrl + `api/review/${post_id}/remove_like`),
        likeComparison: (comparison_id, user_id) => (baseUrl + `api/${user_id}/like/comparisons/${comparison_id}`),
        deleteComment: (comment_id) => (baseUrl + `api/review/${comment_id}/delete`),
        likeComment: (comment_id) => (baseUrl + `api/review/${comment_id}/like`),
        unlikeComment: (comment_id) => (baseUrl + `api/review/${comment_id}/remove_like`),
        pinComment: (comment_id, post_id) => (baseUrl + `api/review/${comment_id}/pin/${post_id}`),
        unpinComment: (comment_id, post_id) => (baseUrl + `api/review/post/${post_id}/comment/${comment_id}/remove_pin`),
        getComments: (post_id) =>(baseUrl + `api/review/${post_id}/comments`),
        // calling more comments (duh)
        getMoreComments: (comment_id) => (baseUrl + `api/review/comments/${comment_id}/replies`),
        getFeed: () => (baseUrl + `api/posts`)
    },
    books: {
        // for book page
        getBookPage: (book_id) => (baseUrl + `api/books/${book_id}`)
        
    }
}