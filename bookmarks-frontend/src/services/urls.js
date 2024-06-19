let baseUrl = import.meta.env.VITE_BASE_URL;
let wsUrl = import.meta.env.VITE_WS_URL;

// For later when we want to add 
// if (process.env.ENV === 'prod') {
//     baseUrl = 'arbitraryName'
//      wsUrl = 'arbitraryName'
// }

export const urls = {
    // Note there is an extra slash after base so dont start paths with slash
    baseUrl: baseUrl,
    setup: {
        name: baseUrl + 'setup-reader/name',
        bookByText: (text) => (`${baseUrl}books/${text}`),
    },
    authUrl: baseUrl + 'api/auth/verify',
    booksByN: baseUrl + 'books/n/',
    login: baseUrl + 'api/auth/login',
    author: baseUrl + 'api/author/',
    user: {
        // Specific for the current users info
        getUser: (user_id) => (baseUrl + `api/user/${user_id}/get_user`),
        setUserImgCdnUrl: (user_id) => (baseUrl + `api/user/${user_id}/update_profile_img`),
        getUserAbout: (user_id) => (baseUrl + `api/user/${user_id}/user_about`),
        updateUsername: (user_id) => (baseUrl + `api/user/${user_id}/update_username`),
        updateBio: (user_id) => (baseUrl +  `api/user/${user_id}/update_bio`),
        updateEmail: (user_id) => (baseUrl + `api/user/${user_id}/update_email`),
        // Friending, requesting, social stuff.
        sendAnonFriendRequest: (user_id, friend_id) => (baseUrl + `api/user/${user_id}/send_friend_request/${friend_id}`),
        acceptAnonFriendRequest: (user_id, friend_id) => (baseUrl + `api/user/${user_id}/accept_friend_request/${friend_id}`),
        unsendAnonFriendRequest: (user_id, friend_id) => (baseUrl + `api/user/${user_id}/unsend_friend_request/${friend_id}`),
        declineAnonFriendRequest: (user_id, friend_id) => (baseUrl + `api/user/${user_id}/decline_friend_request/${friend_id}`),
        blockAnonFriendRequest: (user_id) => (baseUrl + `api/user/${user_id}/block`),
        getActivitiesForUser: (user_id) => (baseUrl + `api/user/${user_id}/activity`),
        unfriendFriend: (user_id, friend_id) => (baseUrl + `api/user/${user_id}/remove_friend/${friend_id}`),
        followUser: (user_id, friend_id) => (baseUrl + `api/user/${user_id}/follow/${friend_id}`),
        unfollowUser: (user_id, friend_id) => (baseUrl + `api/user/${user_id}/unfollow/${friend_id}`),
        getUsersFriendRequests: (user_id) => (baseUrl + `api/user/${user_id}/friend_requests`),
        searchUsersFriends: (param) => (baseUrl + `api/search/friends/${param}`),
        getFriends: (user_id) => (baseUrl + `api/user/${user_id}/friends`),
    },
    create: {
        searchBook: (text) => (`${baseUrl}api/search/book/${text}`)
    },
    reviews: {
        review: baseUrl + 'api/posts/create_review',
        update: baseUrl + 'api/posts/create_update',
        comparison: baseUrl + 'api/posts/create_comparison',
        createComment: () => (baseUrl + 'api/posts/comment/create'),
        // used in feed
        getReviews: (user_id) => (baseUrl +`api/${user_id}/posts/`),
        getComparisons: (user_id) => (baseUrl + `api/${user_id}/comparisons`),
        // getting post data including initial comments on click of comment btn
        getPost: (post_id) => (baseUrl + `api/posts/post/${post_id}`),
        likePost: (post_id) => (baseUrl + `api/posts/post/${post_id}/like`),
        unlikePost: (post_id) => (baseUrl + `api/posts/post/${post_id}/remove_like`),
        likeComparison: (comparison_id, user_id) => (baseUrl + `api/${user_id}/like/comparisons/${comparison_id}`),
        deletePost: (post_id) => (baseUrl + `api/posts/post/${post_id}/delete`),
        deleteComment: (comment_id) => (baseUrl + `api/review/${comment_id}/delete`),
        likeComment: (comment_id) => (baseUrl + `api/posts/comment/${comment_id}/like`),
        unlikeComment: (comment_id) => (baseUrl + `api/posts/comment/${comment_id}/remove_like`),
        pinComment: (comment_id, post_id) => (baseUrl + `api/posts/post/${post_id}/pin/${comment_id}`),
        unpinComment: (comment_id, post_id) => (baseUrl + `api/review/post/${post_id}/comment/${comment_id}/remove_pin`),
        getComments: (post_id) =>(baseUrl + `api/posts/post/${post_id}/comments`),
        // calling more comments (duh)
        getMoreComments: (comment_id) => (baseUrl + `api/review/comments/${comment_id}/replies`),
        getFeed: () => (baseUrl + `api/posts/`),
    },
    books: {
        // for book page
        getBookPage: (book_id) => (baseUrl + `api/books/${book_id}`)
    },
    rtc: {
        bookshelf: (bookshelf_id, token) => (wsUrl + `api/bookshelves/ws/${bookshelf_id}?token=${token}`),
        createBookshelf: () => (baseUrl + `api/bookshelf/create`),
        createBookshelf: () => (baseUrl + `api/bookshelves/create`),
        bookShelfTest: (bookshelf_id) => (baseUrl + `api/bookshelves/${bookshelf_id}`),
        minimalBookshelvesForLoggedInUser: (user_id) => (baseUrl + `api/bookshelves/minimal_shelves_for_user/${user_id}`),
        getBookshelvesCreatedByUser: (user_id) => (baseUrl + `api/bookshelves/created_bookshelves/${user_id}`),
        getMemberBookshelves: (user_id) => (baseUrl + `api/bookshelves/member_bookshelves/${user_id}`),
        getExploreBookshelves: (user_id) => (baseUrl + `api/bookshelves/explore/${user_id}`),
        getWantToRead: (user_id) => (baseUrl +  `api/bookshelves/want_to_read/${user_id}`),
        /**
         *  @param { obj[str] { contributor_id: contributor_id } }  - the user id of the person you want to add as a contributor to the shelf
         * contributors have write access to shelves. 
         **/ 
        setContributorOnShelf: (bookshelf_id) => (baseUrl + `api/bookshelves/${bookshelf_id}/add_contributor`),
        removeContributorFromShelf: (bookshelf_id) => (baseUrl + `api/bookshelves/${bookshelf_id}/remove_contributor`),
        getBookshelfContributors: (bookshelf_id) => (baseUrl + `api/bookshelves/${bookshelf_id}/contributors`),
        
        setMemberOnShelf: (bookshelf_id) => (baseUrl + `api/bookshelves/${bookshelf_id}/add_member`),
        removeMemberFromShelf: (bookshelf_id) => (baseUrl + `api/bookshelves/${bookshelf_id}/remove_member`),
        
        getBookshelfMembers: (bookshelf_id) => (baseUrl + `api/bookshelves/${bookshelf_id}/members`),
        // Used for updating properties on a shelf.
        setShelfTitle: (bookshelf_id) => (baseUrl + `api/bookshelves/${bookshelf_id}/update_name`),
        setShelfDescription: (bookshelf_id) => (baseUrl + `api/bookshelves/${bookshelf_id}/update_name`),
        setShelfVisibility: (bookshelf_id) => (baseUrl + `api/bookshelves/${bookshelf_id}/update_visibility`),
        // ⚠️⚠️⚠️ Danger zone ⚠️⚠️⚠️.
        deleteBookshelf: (bookshelf_id) => (baseUrl + `api/bookshelves/${bookshelf_id}/delete`),
        quickAddBook: (bookshelf_id) => (baseUrl + `api/bookshelves/quick_add/${bookshelf_id}`),
        getBookshelfWsToken: (bookshelf_id) => (baseUrl + `api/bookshelves/${bookshelf_id}/get_token`),
        updateBookNoteForShelf: (bookshelf_id) => (baseUrl + `api/bookshelves/${bookshelf_id}/update_book_note`),
    },
}

// Methods for navigating to and from places.
export const navRoutes = { 
    toLoggedInFeed: (current_user) => (`/feed/${current_user}/all`), 
    toUserPageFromPost: (current_user, user) => (`/feed/${current_user}/user/${user}`),
    toBookPageFromPost: (current_user, book_id) => (`/feed/${current_user}/works/${book_id}`),
    toPostPageFromFeed: (current_user, post_id) => (`/feed/${current_user}/post/${post_id}`),
    toBookshelfSectionPage: (current_user, shelfType) => (`/feed/${current_user}/bookshelves/by/${shelfType}`),
}