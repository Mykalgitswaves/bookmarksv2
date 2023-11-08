<template>
    <transition-group tag="div" name="content">
        <div v-if="postType === 'ComparisonPost'" class="center-cards">
            <ComparisonPost 
              :book="p.book"
              :small_img_url="p.book_small_img"
              :headlines="p.book_specific_headlines"
              :book_title="p.book_title"
              :comparisons="p.responses"
              :comparators="p.comparators"
              :comparator_ids="p.comparators"
              :created_at="p.created_date"
              :id="p.id"
              :username="p.user_username"
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
            />
          </div>
          <div class="flex content-center px-2">
            <div class="make-comments-container main">
                <textarea 
                    class="make-comment-textarea"
                    type="text"
                    v-model="comment"
                    placeholder="Be nice, be thoughtful"    
                />

                <button
                    class="send-comment-btn" 
                    type="button"
                    @click="postComment()"
                >
                    <IconSend />
                </button>
            </div>
          </div>

          <Comments v-if="p && comments.length" :comments="comments" :post-id="p.id" :post-username="p.user_username"/>

          <div class="mobile-menu-spacer sm:hidden"></div>
    </transition-group>
</template>
<script setup>
import { ref, reactive } from 'vue'
import { useRoute } from 'vue-router';
import { urls } from '../../services/urls'; 
import { db } from '../../services/db';
import IconSend from '../svg/icon-send.vue';
import Comments from './posts/comments.vue';
import ComparisonPost from './posts/comparisonPost.vue';
import UpdatePost from './posts/updatePost.vue';
import ReviewPost from './posts/ReviewPost.vue';

// Grab data from and put into a new object so we dont need to load post again

// This is for modeling comments and sending to backend
const p = ref(null);
const postType = ref('');
const comments = ref([]);

const request = reactive({
    "skip": 0,
    "limit": 20,
});

const route = useRoute();
const { user, post } = route.params;

async function get_post_and_comments() {
    await db.get(urls.reviews.getPost(user, post)).then((res) => {
        p.value = res.data.post;
        postType.value = res.data.post_type;
    });
    
    await db.get(urls.reviews.getComments(post), request, true).then((res) => {
        comments.value = res.data
    })
}

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

    if(comment.value.length > 1){
        await db.post(urls.reviews.createComment(), data, true).then((res) => {
            comments.value.push({"comment": res.data})
        });
    };
};

</script>
