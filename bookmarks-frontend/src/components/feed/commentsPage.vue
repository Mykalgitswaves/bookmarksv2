<template>
    <BackBtn/>
    <transition-group tag="div" name="content">
        <div v-if="postType === 'ComparisonPost'" class="center-cards">
            <ComparisonPost 
                :bookBlobs="p.compared_books"
                :headlines="p.book_specific_headlines"
                :comparisons="p.responses"
                :comparators="p.comparators"
                :createdDate="p.created_date"
                :user_id="p.user_id"
                :id="p.id"
                :username="p.user_username"
                :num_replies="p.num_replies"
                :likes="p.likes"
            />
          </div>

          <div v-if="postType === 'ReviewPost'" class="center-cards">
            <ReviewPost
              :id="p.id"
              :book="p.book"
              :title="p.book_title"
              :headline="p.headline"
              :question_ids="p.question_ids"
              :questions="p.questions"
              :responses="p.responses"
              :spoilers="p.spoilers"
              :username="p.user_username"
              :small_img_url="p.book_small_img"
              :num_replies="p.num_replies"
              :likes="p.likes"
            />
          </div>

          <div v-if="postType === 'UpdatePost'" class="center-cards">
            <UpdatePost
              :id="p.id"
              :book="p.book"
              :title="p.book_title"
              :headline="p.headline"
              :response="p.response"
              :spoiler="p.spoiler"
              :username="p.user_username"
              :small_img_url="p.book_small_img"
              :page="p.page"
              :num_replies="p.num_replies"
              :likes="p.likes"
            />
          </div>

          <div v-if="p" class="grid content-center px-2 my-5">
            <p class="text-sm italic text-slate-600">
                "The trouble with most of us is that we would rather be ruined by praise than saved by criticism."
            </p>   
            <div class="make-comments-container main">
                <label for="post-comment-form">
                    <textarea 
                        id="post-comment-form"  
                        class="make-comment-textarea"
                        type="text"
                        v-model="comment"
                        :placeholder="placeholders[randomPlaceholderIndex]"    
                    />
                </label>

                <button
                    class="send-comment-btn" 
                    type="button"
                    @click="postComment()"
                >
                    <IconSend />
                </button>
            </div>
          </div>

          <Comments v-if="p" 
            :comments="comments" 
            :pinned-comments="pinnedComments" 
            :post-id="p.id" 
            :op-user-uuid="op_user_uuid" 
            @comment-deleted="commentDeleted"
        />

          <div class="mobile-menu-spacer sm:hidden"></div>
    </transition-group>
</template>
<script setup>
import { ref, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router';
import { urls } from '../../services/urls'; 
import { db } from '../../services/db';
import BackBtn from './partials/back-btn.vue';
import IconSend from '../svg/icon-send.vue';
import Comments from './posts/comments.vue';
import ComparisonPost from './posts/comparisonPost.vue';
import UpdatePost from './posts/updatePost.vue';
import ReviewPost from './posts/ReviewPost.vue';
import { componentMapping } from './createPostService';

// Grab data from and put into a new object so we dont need to load post again

// This is for modeling comments and sending to backend
const p = ref(null);
const postType = ref('');
const op_user_uuid = ref('');
const comments = ref([]);
const pinnedComments = ref([]);

const request = reactive({
    "skip": 0,
    "limit": 20,
});

const route = useRoute();
const router = useRouter();
const { user, post } = route.params;
const uuid = ref('');

async function get_post_and_comments() {
    console.log(post);

    await db.get(urls.reviews.getPost(post)).then((res) => {
        if(res.data === null || undefined){
            return;
        }
        p.value = res.data?.post;
        postType.value = res.data?.post_type;
        op_user_uuid.value = res.data?.op_user_id
    });
    
    await db.get(urls.reviews.getComments(post), request, true).then((res) => {
        if(res.data === null || undefined){
            return;
        }

        comments.value = res.data?.comments
        pinnedComments.value = res.data?.pinned_comments
        uuid.value = res.data?.uuid
    });
};

get_post_and_comments();

const comment = ref('');
const replied_to = ref(null);

async function postComment(){
    const data = {
        "post_id": p.value.id,
        "text": comment.value,
        "pinned": false,
        "replied_to": replied_to.value,
    };
    // cant post empty comment strings.
    if(comment.value.length > 1){
        await db.post(urls.reviews.createComment(), data, true).then((res) => {
            comments.value.push({"comment": res.data})
        });
    };
};

// actual delete happens on db, this just hides from ui before next refresh.
function commentDeleted(comment_id) {
    comments.value = comments.value.filter((c) => c.comment.id !== comment_id);
    pinnedComments.value = pinnedComments.value.filter((c) => c.comment.id !== comment_id);
};

const placeholders = [
    'Penny for your thoughts',
    'Whats on your mind?',
    'Promoting respectfufl discourse',
    'Thoughts, questions, musings?',
    'Xo Xo',
    'Im Charlie Trout'
]

const randomPlaceholderIndex = Math.floor(Math.random() * (placeholders.length - 1) + 1);

</script>


bookBlobs
headlines
comparisons
comparators
createdDate
username
id
isIronic
isAiGeneratedHeadlines
user_id
like