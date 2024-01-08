import PostActivity from './PostActivity.vue';
import CommentActivityContent from './commentActivityContent.vue';
import FriendActivity from './FriendActivity.vue';

export const activityMap = {
    'liked_post': { 
        component: PostActivity,
        props: (data) => ({
            actingUserId: data.acting_user_id,
            actingUserProfileImg: data.acting_user_profile_img_url,
            actingUserUsername: data.acting_user_username,
            createdDate: data.created_date,
            activityType: data.activity_type,
            postId: data.post_id,
            bookSmallImgUrls: data.book_small_img_urls
        })
    },
    'pinned_comment': { 
        component: CommentActivityContent,
        props: (data) => ({
            actingUserId: data.acting_user_id,
            actingUserProfileImg: data.acting_user_profile_img_url,
            actingUserUsername: data.acting_user_username,
            createdDate: data.created_date,
            activityType: data.activity_type,
            postId: data.post_id,
            bookSmallImgUrls: data.book_small_img_urls,
            comment_id: data.comment_id,
            commentText: data.comment_text,
            isPinned: true
        })
    },
    'commented_on_post': { 
        component: CommentActivityContent,
        props: (data) => ({
            actingUserId: data.acting_user_id,
            actingUserProfileImg: data.acting_user_profile_img_url,
            actingUserUsername: data.acting_user_username,
            createdDate: data.created_date,
            activityType: data.activity_type,
            postId: data.post_id,
            bookSmallImgUrls: data.book_small_img_urls,
            commentId: data.comment_id,
            commentText: data.comment_text
        })
    },
    'commentActivities': { 
        component: CommentActivityContent,
        props: (data) => ({
            actingUserId: data.acting_user_id,
            actingUserProfileImg: data.acting_user_profile_img_url,
            actingUserUsername: data.acting_user_username,
            createdDate: data.created_date,
            activityType: data.activity_type,
            postId: data.post_id,
            bookSmallImgUrls: data.book_small_img_urls,
            commentId: data.comment_id,
            commentText: data.comment_text,
            replyId: data.reply_id,
            replyText: data.reply_text,
        })
    },
    'friendActivity': { 
        component: FriendActivity,
        props: (data) => ({
            current_username: data.current_username,
            actingUserId: data.acting_user_id,
            actingUserProfileImg: data.acting_user_profile_img_url,
            actingUserUsername: data.acting_user_username,
            activityType: data.activity_type,
            createdDate: data.created_date
        })
    }
}

// Used to direct activities for their corresponding components in activity ^. 
export function getFormattedActivityType(activityString) {
    if(activityString === 'commented_on_post' | 'replied_to_comment') {
        return 'commentActivities'   
    } else if (activityString === 'friendship') {
        return 'friendActivity'
    } else if(activityString === 'liked_post'){
       return 'liked_post'
    } else {
        return 'pinned_comment'
    }
}

export const activityService = {
    'liked_post': {
        string: 'liked a post', 
        click: (user, post_id, router) => router.push(`/feed/${user}/post/${post_id}`)
    },
    'pinned_comment': {
        string: 'pinned a comment', 
        click: (user, post_id, router) => router.push(`/feed/${user}/post/${post_id}`)
    },
    'commented_on_post': {
        string: 'commented on a post',
        click: (user, post_id, router) => router.push(`/feed/${user}/post/${post_id}`)
    },
    'friendship': {
        string: 'became friends with'
    }
}