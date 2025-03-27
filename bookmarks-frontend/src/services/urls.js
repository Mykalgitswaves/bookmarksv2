let baseUrl = import.meta.env.VITE_BASE_URL;
let wsUrl = import.meta.env.VITE_WS_URL;
// For later when we want to add 
// if (process.env.ENV === 'prod') {
//     baseUrl = 'arbitraryName'
//      wsUrl = 'arbitraryName'
// }

const BOOK_CLUBS_PREFIX = 'api/bookclubs/'
const BOOK_SHELVES_PREFIX = 'api/bookshelves/';

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
    search: {
        general: (searchParam) =>  `${baseUrl}api/search/${searchParam}`,
        bookClub: (searchParam) => (baseUrl + `api/search/bookclubs/${searchParam}`),
        bookshelf: (searchParam) => (baseUrl + `api/search/bookshelves/${searchParam}`),
        user: (searchParam) => (baseUrl + `api/search/users/${searchParam}`)
    },
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
        acceptAnonFriendRequest: (friend_id) => (baseUrl + `api/user/${friend_id}/accept_friend_request`),
        unsendAnonFriendRequest: (user_id, friend_id) => (baseUrl + `api/user/${user_id}/unsend_friend_request/${friend_id}`),
        declineAnonFriendRequest: (friend_id) => (baseUrl + `api/user/${friend_id}/decline_friend_request`),
        blockAnonFriendRequest: (user_id) => (baseUrl + `api/user/${user_id}/block`),
        getActivitiesForUser: (user_id) => (baseUrl + `api/user/${user_id}/activity`),
        unfriendFriend: (user_id, friend_id) => (baseUrl + `api/user/${user_id}/remove_friend/${friend_id}`),
        followUser: (user_id, friend_id) => (baseUrl + `api/user/${user_id}/follow/${friend_id}`),
        unfollowUser: (user_id, friend_id) => (baseUrl + `api/user/${user_id}/unfollow/${friend_id}`),
        getUsersFriendRequests: (user_id) => (baseUrl + `api/user/${user_id}/friend_requests`),
        searchUsersFriends: (param) => (baseUrl + `api/search/friends/${param}`),
        getFriends: (user_id) => (baseUrl + `api/user/${user_id}/friends`),
        getNotificationCount: (user_id) => (baseUrl + `api/user/${user_id}/notifications_count`),
    },
    create: {
        searchBook: (text) => (`${baseUrl}api/search/book/${text}`)
    },
    reviews: {
        review: baseUrl + 'api/posts/create_review',
        update: baseUrl + 'api/posts/create_update',
        comparison: baseUrl + 'api/posts/create_comparison',
        createComment: () => (`${baseUrl}api/posts/comment/create`),
        // used in feed
        getReviews: (user_id) => (baseUrl +`api/${user_id}/posts/`),
        getComparisons: (user_id) => (baseUrl + `api/${user_id}/comparisons`),
        // getting post data including initial comments on click of comment btn
        getPost: (post_id) => (baseUrl + `api/posts/post/${post_id}`),
        likePost: (post_id) => (baseUrl + `api/posts/post/${post_id}/like`),
        unlikePost: (post_id) => (baseUrl + `api/posts/post/${post_id}/remove_like`),
        likeComparison: (comparison_id, user_id) => (baseUrl + `api/${user_id}/like/comparisons/${comparison_id}`),
        deletePost: (post_id) => (baseUrl + `api/posts/post/${post_id}/delete`),
        deleteComment: (comment_id) => (baseUrl + `api/posts/comment/${comment_id}/delete`),
        likeComment: (comment_id) => (baseUrl + `api/posts/comment/${comment_id}/like`),
        unlikeComment: (comment_id) => (baseUrl + `api/posts/comment/${comment_id}/remove_like`),
        pinComment: (comment_id, post_id) => (baseUrl + `api/posts/post/${post_id}/pin/${comment_id}`),
        unpinComment: (comment_id, post_id) => (baseUrl + `api/review/post/${post_id}/comment/${comment_id}/remove_pin`),
        getComments: (post_id) =>(baseUrl + `api/posts/post/${post_id}/comments`),
        // calling more comments (duh)
        getCommentById: (comment_id) => (`${baseUrl}api/review/comments/${comment_id}/comment`),
        getMoreComments: (comment_id) => (baseUrl + `api/review/comments/${comment_id}/replies`),
        // Threads!
        getParentCommentsForComment: (post_id, comment_id) => (`${baseUrl}api/post/${post_id}/comments/${comment_id}/parent_comments`),
        getCommentForComments: (post_id, comment_id) => (`${baseUrl}api/posts/post/${post_id}/comments/${comment_id}`),
        getFeed: () => (baseUrl + `api/posts/`),
    },
    books: {
        // for book page
        getBookPage: (book_id) => (baseUrl + `api/books/${book_id}`)
    },
    rtc: {
        bookshelf: (bookshelf_id, token) => (wsUrl + `${BOOK_SHELVES_PREFIX}ws/${bookshelf_id}?token=${token}`),
        createBookshelf: () => (baseUrl + `${BOOK_SHELVES_PREFIX}create`),
        bookShelfTest: (bookshelf_id) => (baseUrl + `${BOOK_SHELVES_PREFIX}${bookshelf_id}`),
        minimalBookshelvesForLoggedInUser: (user_id) => (baseUrl + `${BOOK_SHELVES_PREFIX}minimal_shelves_for_user/${user_id}`),
        getBookshelvesCreatedByUser: (user_id) => (baseUrl + `${BOOK_SHELVES_PREFIX}created_bookshelves/${user_id}`),
        getMemberBookshelves: (user_id) => (baseUrl + `${BOOK_SHELVES_PREFIX}member_bookshelves/${user_id}`),
        getExploreBookshelves: (user_id) => (baseUrl + `${BOOK_SHELVES_PREFIX}explore/${user_id}`),
        getWantToRead: (user_id) => (baseUrl +  `${BOOK_SHELVES_PREFIX}want_to_read/${user_id}`),
        getCurrentlyReading: (user_id) => (baseUrl + `${BOOK_SHELVES_PREFIX}currently_reading/${user_id}`),
        getCurrentlyReadingPreview: (user_id) => (baseUrl + `${BOOK_SHELVES_PREFIX}currently_reading/${user_id}/preview`),
        getCurrentlyReadingForFeed: (user_id) => (baseUrl + `${BOOK_SHELVES_PREFIX}currently_reading/${user_id}/front_page`),
        getUpdatesForCurrentlyReadingPageRange: (user_id, book_id) => (baseUrl + `${BOOK_SHELVES_PREFIX}currently_reading/${user_id}/currently_reading_book/${book_id}/updates_for_current_page`),
        getProgressBarForBookUpdates: (user_id, book_id) => (baseUrl + `${BOOK_SHELVES_PREFIX}progress_bar/${user_id}/book/${book_id}/updates`),
        setCurrentPageOnCurrentlyReading: (user_id) => (baseUrl + `${BOOK_SHELVES_PREFIX}currently_reading/${user_id}/update_current_page`),
        /**
         *  @param { obj[str] { contributor_id: contributor_id } }  - the user id of the person you want to add as a contributor to the shelf
         * contributors have write access to shelves. 
         **/ 
        setContributorOnShelf: (bookshelf_id) => (baseUrl + `${BOOK_SHELVES_PREFIX}${bookshelf_id}/add_contributor`),
        removeContributorFromShelf: (bookshelf_id) => (baseUrl + `${BOOK_SHELVES_PREFIX}${bookshelf_id}/remove_contributor`),
        getBookshelfContributors: (bookshelf_id) => (baseUrl + `${BOOK_SHELVES_PREFIX}${bookshelf_id}/contributors`),
        
        setMemberOnShelf: (bookshelf_id) => (baseUrl + `${BOOK_SHELVES_PREFIX}${bookshelf_id}/add_member`),
        removeMemberFromShelf: (bookshelf_id) => (baseUrl + `${BOOK_SHELVES_PREFIX}${bookshelf_id}/remove_member`),
        
        getBookshelfMembers: (bookshelf_id) => (baseUrl + `${BOOK_SHELVES_PREFIX}${bookshelf_id}/members`),
        // Used for updating properties on a shelf.
        setShelfTitle: (bookshelf_id) => (baseUrl + `${BOOK_SHELVES_PREFIX}${bookshelf_id}/update_name`),
        setShelfDescription: (bookshelf_id) => (baseUrl + `${BOOK_SHELVES_PREFIX}${bookshelf_id}/update_name`),
        setShelfVisibility: (bookshelf_id) => (baseUrl + `${BOOK_SHELVES_PREFIX}${bookshelf_id}/update_visibility`),
        // ⚠️⚠️⚠️ Danger zone ⚠️⚠️⚠️.
        deleteBookshelf: (bookshelf_id) => (baseUrl + `${BOOK_SHELVES_PREFIX}${bookshelf_id}/delete`),
        quickAddBook: (bookshelf_id) => (baseUrl + `${BOOK_SHELVES_PREFIX}quick_add/${bookshelf_id}`),
        getBookshelfWsToken: (bookshelf_id) => (baseUrl + `${BOOK_SHELVES_PREFIX}${bookshelf_id}/get_token`),
        updateBookNoteForShelf: (bookshelf_id) => (baseUrl + `${BOOK_SHELVES_PREFIX}${bookshelf_id}/update_book_note`),
        removeBookFromShelf: (bookshelf_id, book_id) => (baseUrl + `${BOOK_SHELVES_PREFIX}${bookshelf_id}/remove_book/${book_id}`),
        // Following!
        followPublicBookshelf: (bookshelf_id) => (`${baseUrl}${BOOK_SHELVES_PREFIX}${bookshelf_id}/follow`),
    },
    bookclubs: {
        // Create / POST
        create: () => (baseUrl + `${BOOK_CLUBS_PREFIX}create`),
        createClubUpdate: (bookclub_id) => (`${baseUrl}${BOOK_CLUBS_PREFIX}${bookclub_id}/update/create`),
        startCurrentlyReadingBookForClub: 
            (bookclub_id) => (baseUrl + `${BOOK_CLUBS_PREFIX}${bookclub_id}/currently_reading/start`),
        finishCurrentlyReadingBookForClub: 
            (bookclub_id) => (baseUrl + `${BOOK_CLUBS_PREFIX}${bookclub_id}/currently_reading/finish`),
        stopCurrentlyReadingBookForClub: 
            (bookclub_id) => (baseUrl + `${BOOK_CLUBS_PREFIX}${bookclub_id}/currently_reading/stop`),
        // Read / GETS
        getClubsOwnedByUser: (user_id) =>  (baseUrl + `${BOOK_CLUBS_PREFIX}owned/${user_id}`),
        getClubsJoinedByCurrentUser: (user_id) =>  (baseUrl + `${BOOK_CLUBS_PREFIX}member/${user_id}`),
        getClubFeed: (bookclub_id) => (baseUrl + `${BOOK_CLUBS_PREFIX}${bookclub_id}/feed`),
        // Gets a finished feed for a club the user has finished reading! 
        getFinishedClubFeed: (bookclub_id) => (`${baseUrl}${BOOK_CLUBS_PREFIX}${bookclub_id}/feed/finished`),
        getClubPace: (bookclub_id) => (baseUrl + `${BOOK_CLUBS_PREFIX}${bookclub_id}/club_members_pace`),
        getPaceForUserInClub: (bookclub_id) => (baseUrl + `${BOOK_CLUBS_PREFIX}${bookclub_id}/user_pace`),
        getMinimalClub: (bookclub_id, user_id) => (baseUrl + `${BOOK_CLUBS_PREFIX}${bookclub_id}/minimal_preview/${user_id}/user`),
        getInvitesForClub: (bookclub_id) => (baseUrl + `${BOOK_CLUBS_PREFIX}${bookclub_id}/club_invites`),
        // Get club post for an individual post in a feed (comments page)
        getClubPost: (bookclub_id, post_id) => (`${baseUrl}${BOOK_CLUBS_PREFIX}${bookclub_id}/post/${post_id}`),
        // Sending and loading invitation / member stuff.
        sendInvites: () => (baseUrl + `${BOOK_CLUBS_PREFIX}invite`),
        searchUsersNotInClub: (bookClubId, searchParam) => 
            (baseUrl + `${BOOK_CLUBS_PREFIX}${bookClubId}/search/users/${searchParam}`),
        getMembersForBookClub: (bookclub_id, user_id) => 
            (baseUrl + `${BOOK_CLUBS_PREFIX}${bookclub_id}/members/${user_id}`),
        getCurrentlyReadingForClub: (bookclub_id) => (baseUrl + `${BOOK_CLUBS_PREFIX}${bookclub_id}/currently_reading`),
        setCurrentlyReadingBook: (bookclub_id) => (baseUrl + `${BOOK_CLUBS_PREFIX}${bookclub_id}/currently_reading/start`),
        getPaceForReadersInClub: (bookclub_id) => (baseUrl + `${BOOK_CLUBS_PREFIX}${bookclub_id}/user_pace`),
        previewEmailInvitesForClub: (bookclub_id, type) => (baseUrl + `${BOOK_CLUBS_PREFIX}${bookclub_id}/preview_emails/${type}`),
        // DANGER DUDE
        removeMemberFromBookClub: (bookclub_id) => (baseUrl + `${BOOK_CLUBS_PREFIX}${bookclub_id}/remove_member`),
        // INVITE STUFF
        loadClubDataForInvite: (bookclub_id) => (baseUrl + `${BOOK_CLUBS_PREFIX}${bookclub_id}/club_for_invite`),
        getInvitesForUser: (user_id) =>  (baseUrl + `${BOOK_CLUBS_PREFIX}invites/${user_id}`),
        acceptInviteToBookClub: (invite_id) => (baseUrl + `${BOOK_CLUBS_PREFIX}invites/accept/${invite_id}`),
        declineInviteToBookClub: (invite_id) => (baseUrl + `${BOOK_CLUBS_PREFIX}invites/decline/${invite_id}`),
        // AWARDS
        // optional endpoint object
        // post_id:str
        // current_uses:bool
        // 
        getAwards: (bookclub_id) => (baseUrl + `${BOOK_CLUBS_PREFIX}${bookclub_id}/awards`),
        grantAwardToPost: (bookclub_id, post_id, award_id) => (`${baseUrl}${BOOK_CLUBS_PREFIX}${bookclub_id}/post/${post_id}/award/${award_id}`),
        ungrantAwardToPost: (bookclub_id, post_id, award_id) => (`${baseUrl}${BOOK_CLUBS_PREFIX}${bookclub_id}/post/${post_id}/award/${award_id}`),
        // Bug notifications
        peerPressureMember: (bookclub_id, member_id) => (`${baseUrl}${BOOK_CLUBS_PREFIX}${bookclub_id}/create_notification`),
        getClubNotificationsForUser: (user_id) => (`${baseUrl}${BOOK_CLUBS_PREFIX}notifications_for_clubs/${user_id}`),
        dismissClubNotification: (notification_id) => (`${baseUrl}${BOOK_CLUBS_PREFIX}dismiss_notification/${notification_id}`),
        // Is user finished reading
        getCurrentUserFinishedReading: (bookclub_id, user_id) => (`${baseUrl}${BOOK_CLUBS_PREFIX}${bookclub_id}/is_user_finished_reading/${user_id}`),
        // FINISH THAT THANG!
        postClubReviewAndFinishReading: (bookclub_id, book_club_book_id) => (`${baseUrl}${BOOK_CLUBS_PREFIX}${bookclub_id}/review/create/${book_club_book_id}`),
        updateClubSettings: (bookclub_id) => (`${baseUrl}${BOOK_CLUBS_PREFIX}${bookclub_id}/update_metadata`),
    },
    concatQueryParams: (url, newQueryParams, returnUrl) => {
        if (!url) {
            console.warn('dude youu need a url for queryParams');
            return;
        }

        if (newQueryParams) {
            // Make sure we aren't fucking up this part of the request.
            // if (!url.endsWith('/')) {
            //     url = url + '/';
            // }
            
            url = url + '?' + new URLSearchParams(newQueryParams);
            console.log(url);
            return url;
        }

        if (returnUrl) {
            return url;
        }
    },
}

// Methods for navigating to and from places.
export const navRoutes = { 
    toLoggedInFeed: (current_user) => (`/feed/${current_user}/all`), 
    // Create a post
    toCreatePost: (current_user, postType, bookId) => (bookId ? `/feed/${current_user}/create/${postType}/${bookId}` : `/feed/${current_user}/create/${postType}`),

    toUserPage: (current_user, user) => (`/feed/${current_user}/user/${user}`),
    toBookPageFromPost: (current_user, book_id) => (`/feed/${current_user}/works/${book_id}`),
    toPostPageFromFeed: (current_user, post_id) => (`/feed/${current_user}/post/${post_id}`),
    toBookshelvesMainPage: (current_user) => (`/feed/${current_user}/bookshelves/all`),
    toBookshelvesCreate: (current_user) => (`/feed/${current_user}/bookshelves/create`),
    toBookshelfSectionPage: (current_user, shelfType) => (`/feed/${current_user}/bookshelves/by/${shelfType}`),
    toBookshelfPage: (current_user, bookshelf_id) => (`/feed/${current_user}/bookshelves/${bookshelf_id}`),
    toBookClubsPage: (current_user) => (`/feed/${current_user}/bookclubs/`),
    toCreateClubPage: (current_user) => (`/feed/${current_user}/bookclubs/create/`),
    toBookClubFeed: (current_user, bookclub_id) => (`/feed/${current_user}/bookclubs/${bookclub_id}/`),
    toBookClubCommentPage: (current_user, bookclub_id, post_id) => (`/feed/${current_user}/bookclubs/${bookclub_id}/post/${post_id}`),
    // Used for component routing inside of bookclubs app.
    toSetCurrentlyReadingPage: (current_user, bookclub_id) => 
        (`/feed/${current_user}/bookclubs/${bookclub_id}/settings/currently-reading/set`),
    bookClubSettingsCurrentlyReading: (current_user, bookclub_id) => 
        (`/feed/${current_user}/bookclubs/${bookclub_id}/settings/currently-reading`),
    bookClubSettingsManageMembersIndex: (current_user, bookclub_id) => 
        (`/feed/${current_user}/bookclubs/${bookclub_id}/settings/manage-members`),
    toSubThreadPage: (current_user,bookclub_id,post_id, comment_id) => (`/feed/${current_user}/bookclubs/${bookclub_id}/post/${post_id}/comments/${comment_id}`)
}